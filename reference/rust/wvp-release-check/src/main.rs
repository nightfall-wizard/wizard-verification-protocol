use std::{env, fs, path::PathBuf, process, process::Command};

const VERSION: &str = env!("CARGO_PKG_VERSION");
const PUBLIC_VERIFICATION_KEY_PATH: &str = "keys/release/wvp-release-signing-public.pem";

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
    signature_verification_attempted: Option<bool>,
    signature_verification_passed: Option<bool>,
    signature_verification_error: Option<String>,
    checksum_verification_attempted: Option<bool>,
    checksum_verification_passed: Option<bool>,
    checksum_verification_error: Option<String>,
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
    println!("Status: release metadata, artifact discovery and checksum verification baseline; not an audit.");
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

fn checksum_work_dir(target: &str, tag: &str) -> Result<PathBuf, String> {
    let safe_target = target.replace('/', "_");
    let safe_tag = tag.replace('/', "_");
    let dir = env::current_dir()
        .map_err(|err| format!("could not read current dir: {err}"))?
        .join("target")
        .join(format!(
            "wvp-release-checksum-{}-{}-{}",
            safe_target,
            safe_tag,
            process::id()
        ));

    fs::create_dir_all(&dir).map_err(|err| format!("could not create checksum dir: {err}"))?;
    Ok(dir)
}

fn signature_work_dir(target: &str, tag: &str) -> Result<PathBuf, String> {
    let safe_target = target.replace('/', "_");
    let safe_tag = tag.replace('/', "_");
    let dir = env::current_dir()
        .map_err(|err| format!("could not read current dir: {err}"))?
        .join("target")
        .join(format!(
            "wvp-release-signature-{}-{}-{}",
            safe_target,
            safe_tag,
            process::id()
        ));

    fs::create_dir_all(&dir).map_err(|err| format!("could not create signature dir: {err}"))?;
    Ok(dir)
}

fn verify_checksum_asset(target: &str, tag: &str) -> (Option<bool>, Option<bool>, Option<String>) {
    let dir = match checksum_work_dir(target, tag) {
        Ok(dir) => dir,
        Err(err) => return (Some(true), Some(false), Some(err)),
    };

    let download = Command::new("gh")
        .args(["release", "download", tag, "--repo", target, "--dir"])
        .arg(&dir)
        .arg("--clobber")
        .output();

    let output = match download {
        Ok(output) => output,
        Err(err) => {
            let _ = fs::remove_dir_all(&dir);
            return (
                Some(true),
                Some(false),
                Some(format!("failed to execute gh release download: {err}")),
            );
        }
    };

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();
        let _ = fs::remove_dir_all(&dir);
        return (
            Some(true),
            Some(false),
            Some(format!("gh release download failed: {stderr}")),
        );
    }

    let entries = match fs::read_dir(&dir) {
        Ok(entries) => entries,
        Err(err) => {
            let _ = fs::remove_dir_all(&dir);
            return (
                Some(true),
                Some(false),
                Some(format!("could not read checksum dir: {err}")),
            );
        }
    };

    let mut checksum_file: Option<PathBuf> = None;

    for entry in entries.flatten() {
        let path = entry.path();
        if path
            .file_name()
            .and_then(|name| name.to_str())
            .map(|name| name.ends_with(".sha256"))
            .unwrap_or(false)
        {
            checksum_file = Some(path);
            break;
        }
    }

    let Some(checksum_file) = checksum_file else {
        let _ = fs::remove_dir_all(&dir);
        return (
            Some(true),
            Some(false),
            Some("no .sha256 asset found".to_string()),
        );
    };

    let Some(checksum_name) = checksum_file.file_name().and_then(|name| name.to_str()) else {
        let _ = fs::remove_dir_all(&dir);
        return (
            Some(true),
            Some(false),
            Some("checksum filename is not valid utf-8".to_string()),
        );
    };

    let verify = Command::new("sha256sum")
        .arg("-c")
        .arg(checksum_name)
        .current_dir(&dir)
        .output();

    let output = match verify {
        Ok(output) => output,
        Err(err) => {
            let _ = fs::remove_dir_all(&dir);
            return (
                Some(true),
                Some(false),
                Some(format!("failed to execute sha256sum: {err}")),
            );
        }
    };

    let passed = output.status.success();
    let error = if passed {
        None
    } else {
        Some(String::from_utf8_lossy(&output.stderr).trim().to_string())
    };

    let _ = fs::remove_dir_all(&dir);

    (Some(true), Some(passed), error)
}

fn verify_signature_asset(target: &str, tag: &str) -> (Option<bool>, Option<bool>, Option<String>) {
    let public_key = PathBuf::from(PUBLIC_VERIFICATION_KEY_PATH);

    if !public_key.is_file() {
        return (
            Some(false),
            None,
            Some(format!(
                "public verification key not found at {PUBLIC_VERIFICATION_KEY_PATH}"
            )),
        );
    }

    let dir = match signature_work_dir(target, tag) {
        Ok(dir) => dir,
        Err(err) => return (Some(true), Some(false), Some(err)),
    };

    let download = Command::new("gh")
        .args(["release", "download", tag, "--repo", target, "--dir"])
        .arg(&dir)
        .arg("--clobber")
        .output();

    let output = match download {
        Ok(output) => output,
        Err(err) => {
            let _ = fs::remove_dir_all(&dir);
            return (
                Some(true),
                Some(false),
                Some(format!("failed to execute gh release download: {err}")),
            );
        }
    };

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();
        let _ = fs::remove_dir_all(&dir);
        return (
            Some(true),
            Some(false),
            Some(format!("gh release download failed: {stderr}")),
        );
    }

    let entries = match fs::read_dir(&dir) {
        Ok(entries) => entries,
        Err(err) => {
            let _ = fs::remove_dir_all(&dir);
            return (
                Some(true),
                Some(false),
                Some(format!("could not read signature dir: {err}")),
            );
        }
    };

    let mut signature_file: Option<PathBuf> = None;

    for entry in entries.flatten() {
        let path = entry.path();
        if path
            .file_name()
            .and_then(|name| name.to_str())
            .map(|name| name.ends_with(".sig"))
            .unwrap_or(false)
        {
            signature_file = Some(path);
            break;
        }
    }

    let Some(signature_file) = signature_file else {
        let _ = fs::remove_dir_all(&dir);
        return (
            Some(true),
            Some(false),
            Some("no .sig asset found".to_string()),
        );
    };

    let Some(signature_name) = signature_file.file_name().and_then(|name| name.to_str()) else {
        let _ = fs::remove_dir_all(&dir);
        return (
            Some(true),
            Some(false),
            Some("signature filename is not valid utf-8".to_string()),
        );
    };

    let Some(signed_asset_name) = signature_name.strip_suffix(".sig") else {
        let _ = fs::remove_dir_all(&dir);
        return (
            Some(true),
            Some(false),
            Some("signature asset does not use .sig suffix".to_string()),
        );
    };

    let signed_asset = dir.join(signed_asset_name);

    if !signed_asset.is_file() {
        let _ = fs::remove_dir_all(&dir);
        return (
            Some(true),
            Some(false),
            Some(format!(
                "signed asset not found for signature asset: {signed_asset_name}"
            )),
        );
    }

    let verify = Command::new("openssl")
        .args(["dgst", "-sha256", "-verify"])
        .arg(&public_key)
        .arg("-signature")
        .arg(&signature_file)
        .arg(&signed_asset)
        .output();

    let output = match verify {
        Ok(output) => output,
        Err(err) => {
            let _ = fs::remove_dir_all(&dir);
            return (
                Some(true),
                Some(false),
                Some(format!("failed to execute openssl: {err}")),
            );
        }
    };

    let passed = output.status.success();

    let error = if passed {
        None
    } else {
        let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();
        let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
        let detail = if stderr.is_empty() { stdout } else { stderr };
        Some(format!("openssl signature verification failed: {detail}"))
    };

    let _ = fs::remove_dir_all(&dir);

    (Some(true), Some(passed), error)
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

    let (
        checksum_verification_attempted,
        checksum_verification_passed,
        checksum_verification_error,
    ) = match (&latest_release_tag, checksum_asset_count) {
        (Some(tag), Some(count)) if count > 0 => verify_checksum_asset(target, tag),
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
        (Some(tag), Some(count)) if count > 0 => verify_signature_asset(target, tag),
        (Some(_), Some(0)) => (Some(false), None, None),
        _ => (Some(false), None, None),
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
        signature_verification_attempted,
        signature_verification_passed,
        signature_verification_error,
        checksum_verification_attempted,
        checksum_verification_passed,
        checksum_verification_error,
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

    if meta.checksum_verification_passed == Some(false)
        && meta.checksum_verification_attempted == Some(true)
    {
        return "FAIL";
    }

    if meta.signature_verification_passed == Some(false)
        && meta.signature_verification_attempted == Some(true)
    {
        return "FAIL";
    }

    if meta.release_count == Some(0) {
        return "WARN";
    }

    if meta.checksum_asset_count == Some(0) || meta.signature_asset_count == Some(0) {
        return "WARN";
    }

    if meta.checksum_verification_passed != Some(true) {
        return "WARN";
    }

    if meta.signature_verification_passed != Some(true) {
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
        println!("  \"summary\": \"GitHub release metadata, artifact discovery, checksum verification and signature verification baseline\",");
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
            println!(
                "    \"signature_verification_attempted\": {},",
                json_bool_opt(meta.signature_verification_attempted)
            );
            println!(
                "    \"signature_verification_passed\": {},",
                json_bool_opt(meta.signature_verification_passed)
            );
            println!(
                "    \"signature_verification_error\": {},",
                json_string_opt(&meta.signature_verification_error)
            );
            println!(
                "    \"checksum_verification_attempted\": {},",
                json_bool_opt(meta.checksum_verification_attempted)
            );
            println!(
                "    \"checksum_verification_passed\": {},",
                json_bool_opt(meta.checksum_verification_passed)
            );
            println!(
                "    \"checksum_verification_error\": {},",
                json_string_opt(&meta.checksum_verification_error)
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
            println!("    \"signature_verification_attempted\": null,");
            println!("    \"signature_verification_passed\": null,");
            println!("    \"signature_verification_error\": null,");
            println!("    \"checksum_verification_attempted\": null,");
            println!("    \"checksum_verification_passed\": null,");
            println!("    \"checksum_verification_error\": null,");
            println!("    \"errors\": []");
        }

        println!("  }},");
        println!("  \"limitations\": [");
        println!("    \"not an audit\",");
        println!("    \"release metadata is not security proof\",");
        println!("    \"asset name discovery is not checksum verification\",");
        println!("    \"checksum verification is integrity verification only\",");
        println!("    \"signature asset discovery is not signature verification\",");
        println!("    \"signature verification depends on configured public key\",");
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
        println!("summary: GitHub release metadata, artifact discovery, checksum verification and signature verification baseline");

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
            println!(
                "signature_verification_attempted: {:?}",
                meta.signature_verification_attempted
            );
            println!(
                "signature_verification_passed: {:?}",
                meta.signature_verification_passed
            );
            println!(
                "signature_verification_error: {:?}",
                meta.signature_verification_error
            );
            println!(
                "checksum_verification_attempted: {:?}",
                meta.checksum_verification_attempted
            );
            println!(
                "checksum_verification_passed: {:?}",
                meta.checksum_verification_passed
            );
            println!(
                "checksum_verification_error: {:?}",
                meta.checksum_verification_error
            );

            for error in meta.errors {
                println!("error: {error}");
            }
        }

        println!("limitation: not an audit");
        println!("limitation: release metadata is not security proof");
        println!("limitation: asset name discovery is not checksum verification");
        println!("limitation: checksum verification is integrity verification only");
        println!("limitation: signature asset discovery is not signature verification");
        println!("limitation: signature verification depends on configured public key");
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
            signature_verification_attempted: Some(false),
            signature_verification_passed: None,
            signature_verification_error: None,
            checksum_verification_attempted: Some(false),
            checksum_verification_passed: None,
            checksum_verification_error: None,
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
            signature_verification_attempted: Some(false),
            signature_verification_passed: None,
            signature_verification_error: None,
            checksum_verification_attempted: Some(true),
            checksum_verification_passed: Some(true),
            checksum_verification_error: None,
            errors: vec!["api error".to_string()],
        };

        assert_eq!(status_for(&cfg, Some(&meta)), "FAIL");
    }

    #[test]
    fn status_fails_when_checksum_verification_fails() {
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
            latest_release_asset_count: Some(2),
            checksum_asset_count: Some(1),
            signature_asset_count: Some(0),
            signature_verification_attempted: Some(false),
            signature_verification_passed: None,
            signature_verification_error: None,
            checksum_verification_attempted: Some(true),
            checksum_verification_passed: Some(false),
            checksum_verification_error: Some("checksum mismatch".to_string()),
            errors: Vec::new(),
        };

        assert_eq!(status_for(&cfg, Some(&meta)), "FAIL");
    }

    #[test]
    fn status_warns_when_checksum_passes_but_signature_missing() {
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
            latest_release_asset_count: Some(2),
            checksum_asset_count: Some(1),
            signature_asset_count: Some(0),
            signature_verification_attempted: Some(false),
            signature_verification_passed: None,
            signature_verification_error: None,
            checksum_verification_attempted: Some(true),
            checksum_verification_passed: Some(true),
            checksum_verification_error: None,
            errors: Vec::new(),
        };

        assert_eq!(status_for(&cfg, Some(&meta)), "WARN");
    }

    #[test]
    fn status_warns_when_signature_asset_exists_but_not_verified() {
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
            latest_release_asset_count: Some(3),
            checksum_asset_count: Some(1),
            signature_asset_count: Some(1),
            signature_verification_attempted: Some(false),
            signature_verification_passed: None,
            signature_verification_error: Some(
                "signature asset discovered but signature verification not attempted".to_string(),
            ),
            checksum_verification_attempted: Some(true),
            checksum_verification_passed: Some(true),
            checksum_verification_error: None,
            errors: Vec::new(),
        };

        assert_eq!(status_for(&cfg, Some(&meta)), "WARN");
    }

    #[test]
    fn status_fails_when_signature_verification_fails() {
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
            latest_release_asset_count: Some(3),
            checksum_asset_count: Some(1),
            signature_asset_count: Some(1),
            signature_verification_attempted: Some(true),
            signature_verification_passed: Some(false),
            signature_verification_error: Some("signature verification failed".to_string()),
            checksum_verification_attempted: Some(true),
            checksum_verification_passed: Some(true),
            checksum_verification_error: None,
            errors: Vec::new(),
        };

        assert_eq!(status_for(&cfg, Some(&meta)), "FAIL");
    }

    #[test]
    fn status_info_when_checksum_and_signature_verification_pass() {
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
            latest_release_asset_count: Some(3),
            checksum_asset_count: Some(1),
            signature_asset_count: Some(1),
            signature_verification_attempted: Some(true),
            signature_verification_passed: Some(true),
            signature_verification_error: None,
            checksum_verification_attempted: Some(true),
            checksum_verification_passed: Some(true),
            checksum_verification_error: None,
            errors: Vec::new(),
        };

        assert_eq!(status_for(&cfg, Some(&meta)), "INFO");
    }
}
