use serde_json::Value;
use wvp_release_check::{
    classify::Status,
    model::{Config, ReleaseObservation, RepositoryTarget},
    report::{render_json, LIMITATIONS},
    report_model::{ReleaseCheckReport, REPORT_SCHEMA_VERSION},
};

fn offline_cfg() -> Config {
    Config {
        target: RepositoryTarget::parse("nightfall-wizard/wizard-verification-protocol")
            .expect("valid test target"),
        json: true,
        live: false,
    }
}

fn parse_json_report(out: &str) -> Value {
    serde_json::from_str(out).expect("render_json must produce valid JSON")
}

#[test]
fn report_contract_has_stable_top_level_fields() {
    let cfg = offline_cfg();
    let report = parse_json_report(&render_json(&cfg, Status::Warn, None));

    assert_eq!(report["schema_version"], REPORT_SCHEMA_VERSION);
    assert_eq!(report["tool"], "wvp-release-check");
    assert_eq!(report["version"], env!("CARGO_PKG_VERSION"));
    assert_eq!(
        report["target"],
        "nightfall-wizard/wizard-verification-protocol"
    );
    assert_eq!(report["status"], "WARN");
    assert_eq!(report["classification"], "observed");
    assert_eq!(report["live_inspection"], false);
    assert!(report["summary"]
        .as_str()
        .is_some_and(|value| !value.is_empty()));
    assert!(report["github"].is_object());
    assert!(report["limitations"].is_array());
}

#[test]
fn report_contract_preserves_github_object_shape() {
    let cfg = offline_cfg();
    let report = parse_json_report(&render_json(&cfg, Status::Warn, None));
    let github = report["github"]
        .as_object()
        .expect("github must be an object");

    for key in [
        "repository_found",
        "release_count",
        "tag_count",
        "latest_release_found",
        "latest_release_tag",
        "latest_release_asset_count",
        "checksum_asset_count",
        "signature_asset_count",
        "signature_verification_attempted",
        "signature_verification_passed",
        "signature_verification_error",
        "checksum_verification_attempted",
        "checksum_verification_passed",
        "checksum_verification_error",
        "errors",
    ] {
        assert!(github.contains_key(key), "missing github field: {key}");
    }

    assert!(github["errors"].is_array());
}

#[test]
fn report_contract_status_is_closed_enum() {
    let cfg = offline_cfg();

    for status in [Status::Info, Status::Warn, Status::Fail] {
        let rendered = render_json(&cfg, status, None);
        let report = parse_json_report(&rendered);
        let value = report["status"].as_str().expect("status must be a string");

        assert!(
            matches!(value, "INFO" | "WARN" | "FAIL"),
            "unexpected status value: {value}"
        );
    }
}

#[test]
fn typed_report_matches_rendered_json_contract() {
    let cfg = Config {
        target: RepositoryTarget::parse("owner/repo").expect("valid test target"),
        json: true,
        live: true,
    };
    let observation = ReleaseObservation {
        repository_found: Some(true),
        release_count: Some(1),
        tag_count: Some(1),
        latest_release_found: Some(true),
        latest_release_tag: Some("v1.0.0".to_string()),
        latest_release_asset_count: Some(3),
        checksum_asset_count: Some(1),
        signature_asset_count: Some(1),
        checksum_verification_attempted: Some(true),
        checksum_verification_passed: Some(true),
        signature_verification_attempted: Some(true),
        signature_verification_passed: Some(true),
        errors: Vec::new(),
        ..ReleaseObservation::default()
    };

    let typed = ReleaseCheckReport::from_parts(&cfg, Status::Info, Some(&observation));
    let rendered = parse_json_report(&render_json(&cfg, Status::Info, Some(&observation)));
    let typed_value =
        serde_json::to_value(&typed).expect("typed report must serialize to JSON value");

    assert_eq!(rendered, typed_value);
}

#[test]
fn report_contract_preserves_limitations() {
    let cfg = offline_cfg();
    let report = parse_json_report(&render_json(&cfg, Status::Warn, None));
    let limitations = report["limitations"]
        .as_array()
        .expect("limitations must be array");

    assert_eq!(limitations.len(), LIMITATIONS.len());

    for limitation in LIMITATIONS {
        assert!(
            limitations.iter().any(|value| value == limitation),
            "missing limitation: {limitation}"
        );
    }
}

#[test]
fn checked_schema_file_matches_contract_version() {
    let schema_raw =
        include_str!("../../../../docs/schemas/wvp-release-check-report-v1.schema.json");
    let schema: Value = serde_json::from_str(schema_raw).expect("schema must be valid JSON");

    assert_eq!(schema["properties"]["schema_version"]["const"], 1);
    assert_eq!(schema["properties"]["tool"]["const"], "wvp-release-check");
    assert_eq!(
        schema["properties"]["status"]["enum"],
        serde_json::json!(["INFO", "WARN", "FAIL"])
    );

    let required = schema["required"]
        .as_array()
        .expect("schema required must be array");

    for key in [
        "schema_version",
        "tool",
        "version",
        "target",
        "status",
        "classification",
        "live_inspection",
        "summary",
        "github",
        "limitations",
    ] {
        assert!(
            required.iter().any(|value| value == key),
            "schema missing required key: {key}"
        );
    }
}
