use std::{env, process, process::Command};

const VERSION: &str = env!("CARGO_PKG_VERSION");

#[derive(Debug, Clone, PartialEq, Eq)]
struct Config {
    target: String,
    json: bool,
    live: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct GithubMetadata {
    repository_found: Option<bool>,
    release_count: Option<usize>,
    tag_count: Option<usize>,
    latest_release_found: Option<bool>,
    latest_release_tag: Option<String>,
    latest_release_asset_count: Option<usize>,
    checksum_asset_count: Option<usize>,
    signature_asset_count: Option<usize>,
    errors: Vec<String>,
}

fn parse_args(args: &[String]) -> Result<Config, String> {
    let mut target: Option<String> = None;
    let mut json = false;
    let mut live = false;
    let mut i = 0;

    while i < args.len() {
        match args[i].as_str() {
            "--target" => {
                i += 1;
                let value = args.get(i).ok_or("--target requires owner/repo")?;
                validate_target(value)?;
                target = Some(value.clone());
            }
            "--json" => json = true,
            "--live" => live = true,
            "-h" | "--help" => return Err("HELP".to_string()),
            other => return Err(format!("unknown argument: {other}")),
        }
        i += 1;
    }

    Ok(Config {
        target: target.ok_or("missing --target owner/repo")?,
        json,
        live,
    })
}

fn validate_target(value: &str) -> Result<(), String> {
    let parts: Vec<&str> = value.split('/').collect();

    if parts.len() != 2 || parts[0].is_empty() || parts[1].is_empty() {
        return Err("target must use owner/repo form".to_string());
    }

    Ok(())
}

fn print_help() {
    println!("wvp-release-check {VERSION}");
    println!("Usage: wvp-release-check --target owner/repo [--json] [--live]");
    println!("Status: release metadata and artifact discovery baseline; not an audit.");
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
        .map_err(|err| format!("could not parse count for {endpoint}: {err}"))
}

fn inspect_github(target: &str) -> GithubMetadata {
    let mut errors = Vec::new();

    let repository_found = match gh_api(&format!("repos/{target}"), ".full_name") {
        Ok(full_name) => Some(full_name.eq_ignore_ascii_case(target)),
        Err(err) => {
            errors.push(err);
            Some(false)
        }
    };

    let release_count = match gh_count(&format!("repos/{target}/releases?per_page=100"), "length") {
        Ok(count) => Some(count),
        Err(err) => {
            errors.push(err);
            None
        }
    };

    let tag_count = match gh_count(&format!("repos/{target}/tags?per_page=100"), "length") {
        Ok(count) => Some(count),
        Err(err) => {
            errors.push(err);
            None
        }
    };

    let latest_endpoint = format!("repos/{target}/releases?per_page=1");

    let (
        latest_release_found,
        latest_release_tag,
        latest_release_asset_count,
        checksum_asset_count,
        signature_asset_count,
    ) = match release_count {
        Some(0) => (Some(false), None, Some(0), Some(0), Some(0)),
        Some(_) => {
            let tag = match gh_api(&latest_endpoint, ".[0].tag_name // \"\"") {
                Ok(value) if value.is_empty() => None,
                Ok(value) => Some(value),
                Err(err) => {
                    errors.push(err);
                    None
                }
            };

            let asset_count = match gh_count(&latest_endpoint, "[.[0].assets[]?] | length") {
                Ok(count) => Some(count),
                Err(err) => {
                    errors.push(err);
                    None
                }
            };

            let checksum_count = match gh_count(
                &latest_endpoint,
                r#"[.[0].assets[]? | select(.name | test("(?i)(sha256|sha512|checksums?|digest)"))] | length"#,
            ) {
                Ok(count) => Some(count),
                Err(err) => {
                    errors.push(err);
                    None
                }
            };

            let signature_count = match gh_count(
                &latest_endpoint,
                r#"[.[0].assets[]? | select(.name | test("(?i)(sig|asc|gpg|minisig|signature)"))] | length"#,
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

    GithubMetadata {
        repository_found,
        release_count,
        tag_count,
        latest_release_found,
        latest_release_tag,
        latest_release_asset_count,
        checksum_asset_count,
        signature_asset_count,
        errors,
    }
}

fn status_for(cfg: &Config, metadata: Option<&GithubMetadata>) -> &'static str {
    if !cfg.live {
        return "WARN";
    }

    let Some(meta) = metadata else {
        return "WARN";
    };

    if meta.repository_found == Some(false) || !meta.errors.is_empty() {
        return "FAIL";
    }

    if meta.release_count == Some(0) {
        return "WARN";
    }

    if meta.checksum_asset_count == Some(0) || meta.signature_asset_count == Some(0) {
        return "WARN";
    }

    "INFO"
}

fn json_escape(value: &str) -> String {
    value
        .replace('\\', "\\\\")
        .replace('"', "\\\"")
        .replace('\n', "\\n")
        .replace('\r', "\\r")
        .replace('\t', "\\t")
}

fn json_bool_opt(value: Option<bool>) -> String {
    match value {
        Some(true) => "true".to_string(),
        Some(false) => "false".to_string(),
        None => "null".to_string(),
    }
}

fn json_usize_opt(value: Option<usize>) -> String {
    match value {
        Some(number) => number.to_string(),
        None => "null".to_string(),
    }
}

fn json_string_opt(value: &Option<String>) -> String {
    match value {
        Some(text) => format!("\"{}\"", json_escape(text)),
        None => "null".to_string(),
    }
}

fn print_json_errors(errors: &[String]) {
    println!("    \"errors\": [");
    for (index, error) in errors.iter().enumerate() {
        let comma = if index + 1 == errors.len() { "" } else { "," };
        println!("      \"{}\"{}", json_escape(error), comma);
    }
    println!("    ]");
}

fn print_report(cfg: &Config) {
    let metadata = if cfg.live {
        Some(inspect_github(&cfg.target))
    } else {
        None
    };

    let status = status_for(cfg, metadata.as_ref());

    if cfg.json {
        println!("{{");
        println!("  \"tool\": \"wvp-release-check\",");
        println!("  \"version\": \"{VERSION}\",");
        println!("  \"target\": \"{}\",", json_escape(&cfg.target));
        println!("  \"status\": \"{status}\",");
        println!("  \"classification\": \"observed\",");
        println!("  \"live_inspection\": {},", cfg.live);
        println!("  \"summary\": \"GitHub release metadata and artifact discovery baseline\",");
        println!("  \"github\": {{");

        if let Some(meta) = metadata.as_ref() {
            println!(
                "    \"repository_found\": {},",
                json_bool_opt(meta.repository_found)
            );
            println!(
                "    \"release_count\": {},",
                json_usize_opt(meta.release_count)
            );
            println!("    \"tag_count\": {},", json_usize_opt(meta.tag_count));
            println!(
                "    \"latest_release_found\": {},",
                json_bool_opt(meta.latest_release_found)
            );
            println!(
                "    \"latest_release_tag\": {},",
                json_string_opt(&meta.latest_release_tag)
            );
            println!(
                "    \"latest_release_asset_count\": {},",
                json_usize_opt(meta.latest_release_asset_count)
            );
            println!(
                "    \"checksum_asset_count\": {},",
                json_usize_opt(meta.checksum_asset_count)
            );
            println!(
                "    \"signature_asset_count\": {},",
                json_usize_opt(meta.signature_asset_count)
            );
            print_json_errors(&meta.errors);
        } else {
            println!("    \"repository_found\": null,");
            println!("    \"release_count\": null,");
            println!("    \"tag_count\": null,");
            println!("    \"latest_release_found\": null,");
            println!("    \"latest_release_tag\": null,");
            println!("    \"latest_release_asset_count\": null,");
            println!("    \"checksum_asset_count\": null,");
            println!("    \"signature_asset_count\": null,");
            println!("    \"errors\": []");
        }

        println!("  }},");
        println!("  \"limitations\": [");
        println!("    \"not an audit\",");
        println!("    \"release metadata is not security proof\",");
        println!("    \"asset name discovery is not checksum verification\",");
        println!("    \"signature asset discovery is not signature verification\",");
        println!("    \"no checksum verification yet\",");
        println!("    \"no signature verification yet\",");
        println!("    \"no reproducible build verification yet\"");
        println!("  ]");
        println!("}}");
    } else {
        println!("WVP Release Integrity Report");
        println!("tool: wvp-release-check");
        println!("version: {VERSION}");
        println!("target: {}", cfg.target);
        println!("status: {status}");
        println!("classification: observed");
        println!("live_inspection: {}", cfg.live);
        println!("summary: GitHub release metadata and artifact discovery baseline");

        if let Some(meta) = metadata {
            println!("repository_found: {:?}", meta.repository_found);
            println!("release_count: {:?}", meta.release_count);
            println!("tag_count: {:?}", meta.tag_count);
            println!("latest_release_found: {:?}", meta.latest_release_found);
            println!("latest_release_tag: {:?}", meta.latest_release_tag);
            println!(
                "latest_release_asset_count: {:?}",
                meta.latest_release_asset_count
            );
            println!("checksum_asset_count: {:?}", meta.checksum_asset_count);
            println!("signature_asset_count: {:?}", meta.signature_asset_count);
            for error in meta.errors {
                println!("error: {error}");
            }
        }

        println!("limitation: not an audit");
        println!("limitation: release metadata is not security proof");
        println!("limitation: asset name discovery is not checksum verification");
        println!("limitation: signature asset discovery is not signature verification");
        println!("limitation: no checksum verification yet");
        println!("limitation: no signature verification yet");
        println!("limitation: no reproducible build verification yet");
    }
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();

    match parse_args(&args) {
        Ok(cfg) => print_report(&cfg),
        Err(err) if err == "HELP" => print_help(),
        Err(err) => {
            eprintln!("ERROR: {err}");
            print_help();
            process::exit(2);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_target() {
        let args = vec!["--target".to_string(), "owner/repo".to_string()];
        let cfg = parse_args(&args).unwrap();
        assert_eq!(cfg.target, "owner/repo");
        assert!(!cfg.json);
        assert!(!cfg.live);
    }

    #[test]
    fn parses_json() {
        let args = vec![
            "--target".to_string(),
            "owner/repo".to_string(),
            "--json".to_string(),
        ];
        let cfg = parse_args(&args).unwrap();
        assert!(cfg.json);
    }

    #[test]
    fn parses_live() {
        let args = vec![
            "--target".to_string(),
            "owner/repo".to_string(),
            "--live".to_string(),
        ];
        let cfg = parse_args(&args).unwrap();
        assert!(cfg.live);
    }

    #[test]
    fn rejects_missing_target() {
        let args: Vec<String> = vec![];
        assert!(parse_args(&args).is_err());
    }

    #[test]
    fn rejects_bad_target_shape() {
        let args = vec!["--target".to_string(), "repo-only".to_string()];
        assert!(parse_args(&args).unwrap_err().contains("owner/repo"));
    }

    #[test]
    fn rejects_empty_owner() {
        let args = vec!["--target".to_string(), "/repo".to_string()];
        assert!(parse_args(&args).unwrap_err().contains("owner/repo"));
    }

    #[test]
    fn rejects_empty_repo() {
        let args = vec!["--target".to_string(), "owner/".to_string()];
        assert!(parse_args(&args).unwrap_err().contains("owner/repo"));
    }

    #[test]
    fn status_warns_when_live_repo_has_no_releases() {
        let cfg = Config {
            target: "owner/repo".to_string(),
            json: true,
            live: true,
        };
        let meta = GithubMetadata {
            repository_found: Some(true),
            release_count: Some(0),
            tag_count: Some(0),
            latest_release_found: Some(false),
            latest_release_tag: None,
            latest_release_asset_count: Some(0),
            checksum_asset_count: Some(0),
            signature_asset_count: Some(0),
            errors: Vec::new(),
        };

        assert_eq!(status_for(&cfg, Some(&meta)), "WARN");
    }

    #[test]
    fn status_fails_when_live_errors_exist() {
        let cfg = Config {
            target: "owner/repo".to_string(),
            json: true,
            live: true,
        };
        let meta = GithubMetadata {
            repository_found: Some(true),
            release_count: Some(1),
            tag_count: Some(1),
            latest_release_found: Some(true),
            latest_release_tag: Some("v1.0.0".to_string()),
            latest_release_asset_count: Some(1),
            checksum_asset_count: Some(1),
            signature_asset_count: Some(1),
            errors: vec!["api error".to_string()],
        };

        assert_eq!(status_for(&cfg, Some(&meta)), "FAIL");
    }
}
