use crate::{
    classify::Status,
    model::{Config, ReleaseObservation},
    report_model::ReleaseCheckReport,
    SUMMARY, TOOL_NAME, VERSION,
};
use serde_json::json;
use std::fmt::Write;

pub use crate::report_model::REPORT_LIMITATIONS as LIMITATIONS;

pub fn render_json(
    cfg: &Config,
    status: Status,
    observation: Option<&ReleaseObservation>,
) -> String {
    let report = ReleaseCheckReport::from_parts(cfg, status, observation);

    match serde_json::to_string_pretty(&report) {
        Ok(mut out) => {
            out.push('\n');
            out
        }
        Err(err) => {
            let fallback = json!({
                "schema_version": 1,
                "tool": TOOL_NAME,
                "version": VERSION,
                "target": cfg.target.to_string(),
                "status": "FAIL",
                "classification": "serialization_error",
                "live_inspection": cfg.live,
                "summary": SUMMARY,
                "github": ReleaseObservation::default(),
                "limitations": [
                    "internal JSON serialization error",
                    err.to_string()
                ]
            });
            format!("{fallback}\n")
        }
    }
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
                .expect("valid test target"),
            json: true,
            live: false,
        };
        let out = render_json(&cfg, Status::Warn, None);
        assert!(out.contains("\"schema_version\": 1"));
        assert!(out.contains("\"tool\": \"wvp-release-check\""));
        assert!(out.contains("\"version\": \"0.3.0\""));
        assert!(out.contains("\"target\": \"nightfall-wizard/wizard-verification-protocol\""));
        assert!(out.contains("\"status\": \"WARN\""));
        assert!(out.contains("\"classification\": \"observed\""));
        assert!(out.contains("\"live_inspection\": false"));
        assert!(out.contains("\"repository_found\": null"));
        assert!(out.contains("\"errors\": []"));
        assert!(out.contains("\"not an audit\""));
    }

    #[test]
    fn json_escapes_error_strings() {
        let cfg = Config {
            target: RepositoryTarget::parse("owner/repo").expect("valid test target"),
            json: true,
            live: true,
        };
        let meta = ReleaseObservation {
            errors: vec!["quote \" newline\n tab\t slash\\".to_string()],
            ..ReleaseObservation::default()
        };
        let out = render_json(&cfg, Status::Fail, Some(&meta));
        let parsed: serde_json::Value =
            serde_json::from_str(&out).expect("render_json must emit valid JSON");
        assert_eq!(
            parsed["github"]["errors"][0],
            "quote \" newline\n tab\t slash\\"
        );
    }
}
