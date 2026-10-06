use serde::Serialize;
use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Config {
    pub target: RepositoryTarget,
    pub json: bool,
    pub live: bool,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct RepositoryTarget {
    pub owner: String,
    pub repo: String,
}

impl RepositoryTarget {
    pub fn parse(value: &str) -> Result<Self, String> {
        let parts: Vec<&str> = value.split('/').collect();
        if parts.len() != 2 {
            return Err("target must use owner/repo form".to_string());
        }
        validate_segment(parts[0], "owner")?;
        validate_segment(parts[1], "repo")?;
        Ok(Self {
            owner: parts[0].to_string(),
            repo: parts[1].to_string(),
        })
    }
}

impl fmt::Display for RepositoryTarget {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}/{}", self.owner, self.repo)
    }
}

fn validate_segment(value: &str, label: &str) -> Result<(), String> {
    if value.is_empty() {
        return Err(format!("{label} must not be empty"));
    }
    if value == "." || value == ".." || value.contains("..") {
        return Err(format!("{label} must not contain path traversal"));
    }
    let valid = value
        .bytes()
        .all(|b| b.is_ascii_alphanumeric() || matches!(b, b'-' | b'_' | b'.'));
    if !valid {
        return Err(format!(
            "{label} contains unsupported characters; allowed: A-Z a-z 0-9 . _ -"
        ));
    }
    Ok(())
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Default)]
pub struct ReleaseObservation {
    pub repository_found: Option<bool>,
    pub release_count: Option<usize>,
    pub tag_count: Option<usize>,
    pub latest_release_found: Option<bool>,
    pub latest_release_tag: Option<String>,
    pub latest_release_asset_count: Option<usize>,
    pub checksum_asset_count: Option<usize>,
    pub signature_asset_count: Option<usize>,
    pub signature_verification_attempted: Option<bool>,
    pub signature_verification_passed: Option<bool>,
    pub signature_verification_error: Option<String>,
    pub checksum_verification_attempted: Option<bool>,
    pub checksum_verification_passed: Option<bool>,
    pub checksum_verification_error: Option<String>,
    pub errors: Vec<String>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_owner_repo_target() {
        let target = RepositoryTarget::parse("owner/repo").unwrap();
        assert_eq!(target.owner, "owner");
        assert_eq!(target.repo, "repo");
        assert_eq!(target.to_string(), "owner/repo");
    }

    #[test]
    fn rejects_bad_targets() {
        for value in [
            "repo-only",
            "/repo",
            "owner/",
            "../repo",
            "owner/../repo",
            "owner/re..po",
        ] {
            assert!(RepositoryTarget::parse(value).is_err(), "{value}");
        }
    }

    #[test]
    fn rejects_shell_control_characters() {
        for value in [
            "owner/repo;rm",
            "owner/repo && rm",
            "owner/repo`x`",
            "owner/repo$(x)",
            "owner/repo name",
            "owner/repo\nx",
        ] {
            assert!(RepositoryTarget::parse(value).is_err(), "{value}");
        }
    }
}
