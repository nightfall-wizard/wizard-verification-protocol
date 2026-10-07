use serde_json::Value;
use std::collections::HashSet;
use std::fs;
use std::path::{Path, PathBuf};

const DOC_REL: &str = "docs/security/SECURITY-INVARIANTS.md";
const NEG_DIR_REL: &str = "test-vectors/release-check/negative";

#[test]
fn negative_security_fixtures_are_executable_specification() {
    let repo_root = repo_root();
    let doc_path = repo_root.join(DOC_REL);
    let neg_dir = repo_root.join(NEG_DIR_REL);

    let doc = fs::read_to_string(&doc_path).expect("security invariant document must exist");

    let allowed_invariants: HashSet<&'static str> = [
        "WVP-INV-001",
        "WVP-INV-002",
        "WVP-INV-003",
        "WVP-INV-004",
        "WVP-INV-005",
        "WVP-INV-006",
        "WVP-INV-007",
    ]
    .iter()
    .copied()
    .collect();

    for invariant in &allowed_invariants {
        assert!(
            doc.contains(invariant),
            "security invariant document must contain {invariant}"
        );
    }

    let mut fixture_count = 0usize;

    for entry in fs::read_dir(&neg_dir).expect("negative fixture directory must exist") {
        let entry = entry.expect("fixture directory entry must be readable");
        let path = entry.path();

        if path.extension().and_then(|x| x.to_str()) != Some("json") {
            continue;
        }

        let file_name = path
            .file_name()
            .and_then(|x| x.to_str())
            .expect("fixture file name must be valid UTF-8");

        if !file_name.starts_with("FRC-SEC-") {
            continue;
        }

        fixture_count += 1;

        let raw = fs::read_to_string(&path).expect("fixture must be readable");
        let json: Value = serde_json::from_str(&raw).expect("fixture must be valid JSON");

        assert_eq!(
            str_field(&json, "expected"),
            Some("reject"),
            "{file_name} must explicitly expect reject"
        );

        let case_id = str_field(&json, "case_id").expect("fixture must have case_id");
        assert!(
            file_name.starts_with(case_id),
            "{file_name} must start with its case_id {case_id}"
        );

        let description = str_field(&json, "description").expect("fixture must have description");
        assert!(
            !description.trim().is_empty(),
            "{file_name} must have non-empty description"
        );

        let invariant = str_field(&json, "invariant").expect("fixture must reference invariant");
        assert!(
            allowed_invariants.contains(invariant),
            "{file_name} references unknown invariant {invariant}"
        );

        assert!(
            doc.contains(invariant),
            "{file_name} references invariant not present in document: {invariant}"
        );

        match invariant {
            "WVP-INV-001" => assert!(
                has_empty_digest(&json),
                "{file_name} must model missing or empty digest material"
            ),
            "WVP-INV-002" => assert!(
                contains_unsafe_path_string(&json),
                "{file_name} must model unsafe artifact path"
            ),
            "WVP-INV-003" => assert!(
                has_duplicate_artifact_identity(&json),
                "{file_name} must model duplicate artifact identity"
            ),
            "WVP-INV-004" => assert!(
                has_verified_without_signature(&json),
                "{file_name} must model unverifiable signature state"
            ),
            "WVP-INV-005" => assert!(
                has_requires_network_true(&json),
                "{file_name} must model network-dependent verification"
            ),
            "WVP-INV-006" => assert!(
                has_silent_downgrade(&json),
                "{file_name} must model silent verification downgrade"
            ),
            "WVP-INV-007" => assert!(
                has_ambiguous_network_context(&json),
                "{file_name} must model ambiguous network or chain context"
            ),
            other => panic!("unhandled invariant {other} in {file_name}"),
        }
    }

    assert!(
        fixture_count >= 7,
        "expected at least 7 negative security fixtures, found {fixture_count}"
    );
}

#[test]
fn negative_fixture_directory_is_version_controlled() {
    let repo_root = repo_root();

    assert!(
        repo_root.join(NEG_DIR_REL).exists(),
        "negative fixture directory must exist"
    );

    assert!(
        repo_root.join(DOC_REL).exists(),
        "security invariant document must exist"
    );
}

fn repo_root() -> PathBuf {
    let mut dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));

    loop {
        if dir.join(DOC_REL).exists() && dir.join(NEG_DIR_REL).exists() {
            return dir;
        }

        if !dir.pop() {
            panic!("could not locate repository root containing {DOC_REL} and {NEG_DIR_REL}");
        }
    }
}

fn str_field<'a>(json: &'a Value, key: &str) -> Option<&'a str> {
    json.get(key).and_then(Value::as_str)
}

fn has_empty_digest(json: &Value) -> bool {
    match json {
        Value::Object(map) => map.iter().any(|(key, value)| {
            (key == "digest" && value.as_str() == Some("")) || has_empty_digest(value)
        }),
        Value::Array(values) => values.iter().any(has_empty_digest),
        _ => false,
    }
}

fn contains_unsafe_path_string(json: &Value) -> bool {
    match json {
        Value::String(s) => {
            s.contains("../")
                || s.contains("..\\")
                || s.starts_with('/')
                || s.contains(":\\")
                || s.contains("././../../")
        }
        Value::Object(map) => map.values().any(contains_unsafe_path_string),
        Value::Array(values) => values.iter().any(contains_unsafe_path_string),
        _ => false,
    }
}

fn has_duplicate_artifact_identity(json: &Value) -> bool {
    let artifacts = match json.get("artifacts").and_then(Value::as_array) {
        Some(artifacts) => artifacts,
        None => return false,
    };

    let mut seen = HashSet::new();

    for artifact in artifacts {
        let name = artifact.get("name").and_then(Value::as_str).unwrap_or("");
        let version = artifact
            .get("version")
            .and_then(Value::as_str)
            .unwrap_or("");
        let identity = format!("{name}@{version}");

        if !seen.insert(identity) {
            return true;
        }
    }

    false
}

fn has_verified_without_signature(json: &Value) -> bool {
    let artifact = match json.get("artifact") {
        Some(artifact) => artifact,
        None => return false,
    };

    artifact.get("claimed_status").and_then(Value::as_str) == Some("verified")
        && artifact.get("signature").and_then(Value::as_str) == Some("")
}

fn has_requires_network_true(json: &Value) -> bool {
    match json {
        Value::Object(map) => map.iter().any(|(key, value)| {
            (key == "requires_network" && value.as_bool() == Some(true))
                || has_requires_network_true(value)
        }),
        Value::Array(values) => values.iter().any(has_requires_network_true),
        _ => false,
    }
}

fn has_silent_downgrade(json: &Value) -> bool {
    let verification = match json.get("verification") {
        Some(verification) => verification,
        None => return false,
    };

    verification
        .get("required_mode")
        .and_then(Value::as_str)
        .is_some()
        && verification
            .get("performed_mode")
            .and_then(Value::as_str)
            .is_some()
        && verification
            .get("downgrade_reported")
            .and_then(Value::as_bool)
            == Some(false)
}

fn has_ambiguous_network_context(json: &Value) -> bool {
    match json {
        Value::String(s) => {
            let lower = s.to_ascii_lowercase();
            lower.contains("mainnet-or-testnet")
                || lower.contains("ambiguous")
                || lower.contains("unknown-network")
        }
        Value::Object(map) => map.values().any(has_ambiguous_network_context),
        Value::Array(values) => values.iter().any(has_ambiguous_network_context),
        _ => false,
    }
}

#[allow(dead_code)]
fn assert_path_exists(path: &Path) {
    assert!(path.exists(), "path must exist: {}", path.display());
}
