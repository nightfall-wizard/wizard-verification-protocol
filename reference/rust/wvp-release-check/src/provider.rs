use crate::{
    error::VerificationError,
    model::{ReleaseObservation, RepositoryTarget},
    verify::{checksum::verify_checksum_asset, signature::verify_signature_asset},
};
use std::process::Command;

pub trait ReleaseEvidenceProvider {
    fn observe(&self, target: &RepositoryTarget) -> ReleaseObservation;
}

#[derive(Debug, Clone, Copy)]
pub struct GhCliProvider;

impl ReleaseEvidenceProvider for GhCliProvider {
    fn observe(&self, target: &RepositoryTarget) -> ReleaseObservation {
        inspect_github(target)
    }
}

fn gh_api(endpoint: &str, jq: &str) -> Result<String, String> {
    let output = Command::new("gh")
        .args(["api", endpoint, "--jq", jq])
        .output()
        .map_err(|err| format!("failed to execute gh: {err}"))?;
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();
        let message = if stderr.is_empty() {
            format!("gh api failed for endpoint: {endpoint}")
        } else {
            format!("gh api failed for endpoint {endpoint}: {stderr}")
        };
        return Err(message);
    }
    Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
}

fn gh_count(endpoint: &str, jq: &str) -> Result<usize, String> {
    let value = gh_api(endpoint, jq)?;
    value
        .parse::<usize>()
        .map_err(|err| VerificationError::CountParse {
            endpoint: endpoint.to_string(),
            detail: err.to_string(),
        })
        .map_err(|err| err.to_string())
}

fn release_query(
    target: &str,
    release_tag: Option<&str>,
) -> Result<(String, &'static str), String> {
    match release_tag {
        None => Ok((format!("repos/{target}/releases?per_page=1"), ".[0]")),
        Some(tag) => {
            if tag.is_empty()
                || tag.len() > 128
                || !tag.as_bytes()[0].is_ascii_alphanumeric()
                || tag.contains("..")
                || !tag
                    .bytes()
                    .all(|b| b.is_ascii_alphanumeric() || matches!(b, b'.' | b'_' | b'-'))
            {
                return Err("invalid WVP_RELEASE_TAG: expected a safe release tag".to_string());
            }
            Ok((format!("repos/{target}/releases/tags/{tag}"), ""))
        }
    }
}

fn inspect_github(target: &RepositoryTarget) -> ReleaseObservation {
    let target_string = target.to_string();
    let mut errors = Vec::new();

    let repository_found = match gh_api(&format!("repos/{target_string}"), ".full_name") {
        Ok(full_name) => Some(full_name.eq_ignore_ascii_case(&target_string)),
        Err(err) => {
            errors.push(err);
            Some(false)
        }
    };

    let release_count = match gh_count(
        &format!("repos/{target_string}/releases?per_page=100"),
        "length",
    ) {
        Ok(count) => Some(count),
        Err(err) => {
            errors.push(err);
            None
        }
    };

    let tag_count = match gh_count(
        &format!("repos/{target_string}/tags?per_page=100"),
        "length",
    ) {
        Ok(count) => Some(count),
        Err(err) => {
            errors.push(err);
            None
        }
    };

    let requested_tag = match std::env::var("WVP_RELEASE_TAG") {
        Ok(tag) => Some(tag),
        Err(std::env::VarError::NotPresent) => None,
        Err(std::env::VarError::NotUnicode(_)) => {
            errors.push("invalid WVP_RELEASE_TAG: non-Unicode value".to_string());
            return ReleaseObservation {
                repository_found,
                release_count,
                tag_count,
                errors,
                ..ReleaseObservation::default()
            };
        }
    };
    let (latest_endpoint, selector) =
        match release_query(&target_string, requested_tag.as_deref()) {
            Ok(query) => query,
            Err(err) => {
                errors.push(err);
                return ReleaseObservation {
                    repository_found,
                    release_count,
                    tag_count,
                    errors,
                    ..ReleaseObservation::default()
                };
            }
        };
    let tag_expression = format!("{selector}.tag_name // \"\"");
    let asset_count_expression = format!("[{selector}.assets[]?] | length");
    let checksum_expression = format!(
        "[{selector}.assets[]? | select(.name | test(\"(?i)(sha256|sha512|checksums?|digest)\"))] | length"
    );
    let signature_expression = format!(
        "[{selector}.assets[]? | select(.name | test(\"(?i)([.](sig|asc|minisig|gpg)$|[.]signature$)\"))] | length"
    );
    let (
        latest_release_found,
        latest_release_tag,
        latest_release_asset_count,
        checksum_asset_count,
        signature_asset_count,
    ) = match release_count {
        Some(0) => (Some(false), None, Some(0), Some(0), Some(0)),
        Some(_) => {
            let tag = match gh_api(&latest_endpoint, &tag_expression) {
                Ok(value) if value.is_empty() => None,
                Ok(value) => Some(value),
                Err(err) => {
                    errors.push(err);
                    None
                }
            };
            let asset_count = match gh_count(&latest_endpoint, &asset_count_expression) {
                Ok(count) => Some(count),
                Err(err) => {
                    errors.push(err);
                    None
                }
            };
            let checksum_count = match gh_count(
                &latest_endpoint,
                &checksum_expression,
            ) {
                Ok(count) => Some(count),
                Err(err) => {
                    errors.push(err);
                    None
                }
            };
            let signature_count = match gh_count(
                &latest_endpoint,
                &signature_expression,
            ) {
                Ok(count) => Some(count),
                Err(err) => {
                    errors.push(err);
                    None
                }
            };
            (
                Some(tag.is_some()),
                tag,
                asset_count,
                checksum_count,
                signature_count,
            )
        }
        None => (None, None, None, None, None),
    };

    if let Some(expected_tag) = requested_tag.as_deref() {
        if latest_release_tag.as_deref() != Some(expected_tag) {
            errors.push(format!(
                "requested WVP release tag {expected_tag} was not returned"
            ));
        }
    }

    let (
        checksum_verification_attempted,
        checksum_verification_passed,
        checksum_verification_error,
    ) = match (&latest_release_tag, checksum_asset_count) {
        (Some(tag), Some(count)) if count > 0 => verify_checksum_asset(&target_string, tag),
        (Some(_), Some(0)) => (
            Some(false),
            Some(false),
            Some("no checksum asset found".to_string()),
        ),
        _ => (Some(false), None, None),
    };

    let (
        signature_verification_attempted,
        signature_verification_passed,
        signature_verification_error,
    ) = match (&latest_release_tag, signature_asset_count) {
        (Some(tag), Some(count)) if count > 0 => verify_signature_asset(&target_string, tag),
        (Some(_), Some(0)) => (Some(false), None, None),
        _ => (Some(false), None, None),
    };

    ReleaseObservation {
        repository_found,
        release_count,
        tag_count,
        latest_release_found,
        latest_release_tag,
        latest_release_asset_count,
        checksum_asset_count,
        signature_asset_count,
        signature_verification_attempted,
        signature_verification_passed,
        signature_verification_error,
        checksum_verification_attempted,
        checksum_verification_passed,
        checksum_verification_error,
        errors,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn default_release_query_preserves_latest_release_behavior() {
        assert_eq!(
            release_query("owner/repo", None),
            Ok(("repos/owner/repo/releases?per_page=1".to_string(), ".[0]"))
        );
    }

    #[test]
    fn selected_release_query_never_falls_back_to_latest() {
        assert_eq!(
            release_query("owner/repo", Some("v0.3.0")),
            Ok(("repos/owner/repo/releases/tags/v0.3.0".to_string(), ""))
        );
    }

    #[test]
    fn selected_release_tag_rejects_unsafe_inputs() {
        for tag in ["", "/bad", "../main", "-bad", "v/1", "x?y", "x#y", "x y"] {
            assert!(release_query("owner/repo", Some(tag)).is_err(), "{tag}");
        }
    }
}
