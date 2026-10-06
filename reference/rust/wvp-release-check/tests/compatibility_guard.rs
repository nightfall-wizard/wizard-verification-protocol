use serde_json::Value;
use std::collections::BTreeSet;
use wvp_release_check::{
    classify::Status,
    model::{Config, RepositoryTarget},
    report::render_json,
    report_model::REPORT_SCHEMA_VERSION,
};

fn offline_cfg() -> Config {
    Config {
        target: RepositoryTarget::parse("nightfall-wizard/wizard-verification-protocol")
            .expect("valid test target"),
        json: true,
        live: false,
    }
}

fn value_kind(value: &Value) -> &'static str {
    match value {
        Value::Null => "null",
        Value::Bool(_) => "boolean",
        Value::Number(_) => "number",
        Value::String(_) => "string",
        Value::Array(_) => "array",
        Value::Object(_) => "object",
    }
}

fn collect_shape(path: &str, value: &Value, out: &mut Vec<String>) {
    match value {
        Value::Null | Value::Bool(_) | Value::Number(_) | Value::String(_) => {
            out.push(format!("{path}:{}", value_kind(value)));
        }
        Value::Array(items) => {
            out.push(format!("{path}:array"));

            if items.is_empty() {
                out.push(format!("{path}[]:<empty>"));
                return;
            }

            let mut element_kinds = BTreeSet::new();
            for item in items {
                element_kinds.insert(value_kind(item));
            }

            for kind in element_kinds {
                out.push(format!("{path}[]:{kind}"));
            }
        }
        Value::Object(map) => {
            out.push(format!("{path}:object"));

            for (key, nested) in map {
                collect_shape(&format!("{path}.{key}"), nested, out);
            }
        }
    }
}

fn rendered_report_shape() -> Vec<String> {
    let rendered = render_json(&offline_cfg(), Status::Warn, None);
    let parsed: Value =
        serde_json::from_str(&rendered).expect("rendered report must be valid JSON");

    assert_eq!(parsed["schema_version"], REPORT_SCHEMA_VERSION);
    assert_eq!(parsed["tool"], "wvp-release-check");
    assert_eq!(parsed["status"], "WARN");

    let mut shape = Vec::new();
    collect_shape("$", &parsed, &mut shape);
    shape.sort();
    shape
}

fn snapshot_shape() -> Vec<String> {
    let mut shape: Vec<String> = include_str!("fixtures/report_contract_v1_shape.txt")
        .lines()
        .filter(|line| !line.trim().is_empty())
        .map(ToOwned::to_owned)
        .collect();

    shape.sort();
    shape
}

#[test]
fn compatibility_guard_report_v1_shape_matches_snapshot() {
    let actual = rendered_report_shape();
    let expected = snapshot_shape();

    assert_eq!(
        actual, expected,
        "report v1 JSON shape changed; update the schema version or intentionally update the snapshot"
    );
}

#[test]
fn compatibility_guard_snapshot_contains_security_relevant_fields() {
    let expected = snapshot_shape();

    for required in [
        "$.schema_version:number",
        "$.status:string",
        "$.github.repository_found:null",
        "$.github.checksum_verification_passed:null",
        "$.github.signature_verification_passed:null",
        "$.github.errors:array",
        "$.limitations:array",
    ] {
        assert!(
            expected.iter().any(|line| line == required),
            "snapshot missing required compatibility guard line: {required}"
        );
    }
}
