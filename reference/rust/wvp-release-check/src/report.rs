use crate::{
    classify::Status,
    model::{Config, ReleaseObservation},
    SUMMARY, TOOL_NAME, VERSION,
};
use serde::Serialize;
use std::fmt::Write;

pub const LIMITATIONS: [&str; 7] = [
    "not an audit",
    "release metadata is not security proof",
    "asset name discovery is not checksum verification",
    "checksum verification is integrity verification only",
    "signature asset discovery is not signature verification",
    "signature verification depends on configured public key",
    "no reproducible build verification yet",
];

fn json_value<T: Serialize>(value: &T) -> String {
    serde_json::to_string(value).expect("WVP JSON serialization must not fail")
}

fn json_line<T: Serialize>(out: &mut String, key: &str, value: &T, comma: bool) {
    let suffix = if comma { "," } else { "" };
    let _ = writeln!(out, "    \"{key}\": {}{suffix}", json_value(value));
}

pub fn render_json(
    cfg: &Config,
    status: Status,
    observation: Option<&ReleaseObservation>,
) -> String {
    let empty = ReleaseObservation::default();
    let meta = observation.unwrap_or(&empty);
    let mut out = String::new();
    let _ = writeln!(out, "{{");
    let _ = writeln!(out, "  \"tool\": {},", json_value(&TOOL_NAME));
    let _ = writeln!(out, "  \"version\": {},", json_value(&VERSION));
    let _ = writeln!(
        out,
        "  \"target\": {},",
        json_value(&cfg.target.to_string())
    );
    let _ = writeln!(out, "  \"status\": {},", json_value(&status.as_str()));
    let _ = writeln!(out, "  \"classification\": \"observed\",");
    let _ = writeln!(out, "  \"live_inspection\": {},", cfg.live);
    let _ = writeln!(out, "  \"summary\": {},", json_value(&SUMMARY));
    let _ = writeln!(out, "  \"github\": {{");
    json_line(&mut out, "repository_found", &meta.repository_found, true);
    json_line(&mut out, "release_count", &meta.release_count, true);
    json_line(&mut out, "tag_count", &meta.tag_count, true);
    json_line(
        &mut out,
        "latest_release_found",
        &meta.latest_release_found,
        true,
    );
    json_line(
        &mut out,
        "latest_release_tag",
        &meta.latest_release_tag,
        true,
    );
    json_line(
        &mut out,
        "latest_release_asset_count",
        &meta.latest_release_asset_count,
        true,
    );
    json_line(
        &mut out,
        "checksum_asset_count",
        &meta.checksum_asset_count,
        true,
    );
    json_line(
        &mut out,
        "signature_asset_count",
        &meta.signature_asset_count,
        true,
    );
    json_line(
        &mut out,
        "signature_verification_attempted",
        &meta.signature_verification_attempted,
        true,
    );
    json_line(
        &mut out,
        "signature_verification_passed",
        &meta.signature_verification_passed,
        true,
    );
    json_line(
        &mut out,
        "signature_verification_error",
        &meta.signature_verification_error,
        true,
    );
    json_line(
        &mut out,
        "checksum_verification_attempted",
        &meta.checksum_verification_attempted,
        true,
    );
    json_line(
        &mut out,
        "checksum_verification_passed",
        &meta.checksum_verification_passed,
        true,
    );
    json_line(
        &mut out,
        "checksum_verification_error",
        &meta.checksum_verification_error,
        true,
    );
    let _ = writeln!(out, "    \"errors\": [");
    for (index, error) in meta.errors.iter().enumerate() {
        let comma = if index + 1 == meta.errors.len() {
            ""
        } else {
            ","
        };
        let _ = writeln!(out, "      {}{}", json_value(error), comma);
    }
    let _ = writeln!(out, "    ]");
    let _ = writeln!(out, "  }},");
    let _ = writeln!(out, "  \"limitations\": [");
    for (index, limitation) in LIMITATIONS.iter().enumerate() {
        let comma = if index + 1 == LIMITATIONS.len() {
            ""
        } else {
            ","
        };
        let _ = writeln!(out, "    {}{}", json_value(limitation), comma);
    }
    let _ = writeln!(out, "  ]");
    let _ = writeln!(out, "}}");
    out
}

pub fn render_text(
    cfg: &Config,
    status: Status,
    observation: Option<&ReleaseObservation>,
) -> String {
    let mut out = String::new();
    let _ = writeln!(out, "WVP Release Integrity Report");
    let _ = writeln!(out, "tool: {TOOL_NAME}");
    let _ = writeln!(out, "version: {VERSION}");
    let _ = writeln!(out, "target: {}", cfg.target);
    let _ = writeln!(out, "status: {}", status.as_str());
    let _ = writeln!(out, "classification: observed");
    let _ = writeln!(out, "live_inspection: {}", cfg.live);
    let _ = writeln!(out, "summary: {SUMMARY}");
    if let Some(meta) = observation {
        let _ = writeln!(out, "repository_found: {:?}", meta.repository_found);
        let _ = writeln!(out, "release_count: {:?}", meta.release_count);
        let _ = writeln!(out, "tag_count: {:?}", meta.tag_count);
        let _ = writeln!(out, "latest_release_found: {:?}", meta.latest_release_found);
        let _ = writeln!(out, "latest_release_tag: {:?}", meta.latest_release_tag);
        let _ = writeln!(
            out,
            "latest_release_asset_count: {:?}",
            meta.latest_release_asset_count
        );
        let _ = writeln!(out, "checksum_asset_count: {:?}", meta.checksum_asset_count);
        let _ = writeln!(
            out,
            "signature_asset_count: {:?}",
            meta.signature_asset_count
        );
        let _ = writeln!(
            out,
            "signature_verification_attempted: {:?}",
            meta.signature_verification_attempted
        );
        let _ = writeln!(
            out,
            "signature_verification_passed: {:?}",
            meta.signature_verification_passed
        );
        let _ = writeln!(
            out,
            "signature_verification_error: {:?}",
            meta.signature_verification_error
        );
        let _ = writeln!(
            out,
            "checksum_verification_attempted: {:?}",
            meta.checksum_verification_attempted
        );
        let _ = writeln!(
            out,
            "checksum_verification_passed: {:?}",
            meta.checksum_verification_passed
        );
        let _ = writeln!(
            out,
            "checksum_verification_error: {:?}",
            meta.checksum_verification_error
        );
        for error in &meta.errors {
            let _ = writeln!(out, "error: {error}");
        }
    }
    for limitation in LIMITATIONS {
        let _ = writeln!(out, "limitation: {limitation}");
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::model::RepositoryTarget;

    #[test]
    fn offline_json_preserves_conformance_surface() {
        let cfg = Config {
            target: RepositoryTarget::parse("nightfall-wizard/wizard-verification-protocol")
                .unwrap(),
            json: true,
            live: false,
        };
        let out = render_json(&cfg, Status::Warn, None);
        assert!(out.contains("\"tool\": \"wvp-release-check\""));
        assert!(out.contains("\"version\": \"0.3.0\""));
        assert!(out.contains("\"target\": \"nightfall-wizard/wizard-verification-protocol\""));
        assert!(out.contains("\"status\": \"WARN\""));
        assert!(out.contains("\"classification\": \"observed\""));
        assert!(out.contains("\"live_inspection\": false"));
        assert!(out.contains("\"repository_found\": null"));
        assert!(out.contains("\"errors\": ["));
        assert!(out.contains("\"not an audit\""));
    }

    #[test]
    fn json_escapes_error_strings() {
        let cfg = Config {
            target: RepositoryTarget::parse("owner/repo").unwrap(),
            json: true,
            live: true,
        };
        let meta = ReleaseObservation {
            errors: vec!["quote \" newline\n tab\t slash\\".to_string()],
            ..ReleaseObservation::default()
        };
        let out = render_json(&cfg, Status::Fail, Some(&meta));
        let parsed: serde_json::Value = serde_json::from_str(&out).unwrap();
        assert_eq!(
            parsed["github"]["errors"][0],
            "quote \" newline\n tab\t slash\\"
        );
    }
}
