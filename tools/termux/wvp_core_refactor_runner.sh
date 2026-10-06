#!/usr/bin/env bash
set -Eeuo pipefail

REPO_URL="https://github.com/nightfall-wizard/wizard-verification-protocol.git"
REPO_DIR="${WVP_REPO_DIR:-$HOME/wizard-verification-protocol}"
BRANCH_BASE="refactor/release-reality-core"
BRANCH="$BRANCH_BASE"

need() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "ERROR: missing command: $1"
    exit 1
  }
}

need git
need cargo
need rustc
need openssl

if [ -d "$REPO_DIR/.git" ]; then
  cd "$REPO_DIR"
else
  git clone "$REPO_URL" "$REPO_DIR"
  cd "$REPO_DIR"
fi

git fetch origin main
git checkout main
git pull --ff-only origin main

if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: working tree is not clean."
  git status --short
  echo
  echo "Fix: commit/stash/delete local changes, then rerun."
  exit 1
fi

if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  BRANCH="${BRANCH_BASE}-$(date +%Y%m%d-%H%M%S)"
fi

git checkout -b "$BRANCH"

CRATE="reference/rust/wvp-release-check"
SRC="$CRATE/src"
mkdir -p "$SRC/verify" docs/architecture docs/threat-model docs/adr docs/review .wvp-backup
cp "$SRC/main.rs" ".wvp-backup/main.rs.before-core-refactor.$(date +%Y%m%d-%H%M%S)"

cat > "$CRATE/Cargo.toml" <<'EOF'
[package]
name = "wvp-release-check"
version = "0.3.0"
edition = "2021"
license = "MIT"
description = "WVP release integrity reference checker bootstrap"

[dependencies]
serde = { version = "1", features = ["derive"] }
serde_json = "1"
EOF

cat > "$SRC/model.rs" <<'EOF'
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
        Ok(Self { owner: parts[0].to_string(), repo: parts[1].to_string() })
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
    let valid = value.bytes().all(|b| b.is_ascii_alphanumeric() || matches!(b, b'-' | b'_' | b'.'));
    if !valid {
        return Err(format!("{label} contains unsupported characters; allowed: A-Z a-z 0-9 . _ -"));
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
        for value in ["repo-only", "/repo", "owner/", "../repo", "owner/../repo", "owner/re..po"] {
            assert!(RepositoryTarget::parse(value).is_err(), "{value}");
        }
    }

    #[test]
    fn rejects_shell_control_characters() {
        for value in ["owner/repo;rm", "owner/repo && rm", "owner/repo`x`", "owner/repo$(x)", "owner/repo name", "owner/repo\nx"] {
            assert!(RepositoryTarget::parse(value).is_err(), "{value}");
        }
    }
}
EOF

cat > "$SRC/error.rs" <<'EOF'
use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum VerificationError {
    Io(String),
    CommandFailed { context: String, detail: String },
    CountParse { endpoint: String, detail: String },
    MissingAsset { suffix: String },
    AmbiguousAsset { label: String, suffix: String, names: String },
    InvalidUtf8Filename(String),
    MissingSignedAsset(String),
    MissingPublicKey(String),
    SignatureVerificationFailed(String),
}

impl fmt::Display for VerificationError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Io(detail) => write!(f, "{detail}"),
            Self::CommandFailed { context, detail } => write!(f, "{context}: {detail}"),
            Self::CountParse { endpoint, detail } => write!(f, "could not parse count for {endpoint}: {detail}"),
            Self::MissingAsset { suffix } => write!(f, "no {suffix} asset found"),
            Self::AmbiguousAsset { label, suffix, names } => write!(f, "multiple {label} assets found for suffix {suffix}: {names}"),
            Self::InvalidUtf8Filename(label) => write!(f, "{label} filename is not valid utf-8"),
            Self::MissingSignedAsset(name) => write!(f, "signed asset not found for signature asset: {name}"),
            Self::MissingPublicKey(path) => write!(f, "public verification key not found at {path}"),
            Self::SignatureVerificationFailed(detail) => write!(f, "openssl signature verification failed: {detail}"),
        }
    }
}
EOF

cat > "$SRC/classify.rs" <<'EOF'
use crate::model::ReleaseObservation;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Status {
    Info,
    Warn,
    Fail,
}

impl Status {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Info => "INFO",
            Self::Warn => "WARN",
            Self::Fail => "FAIL",
        }
    }
}

pub fn status_for(live: bool, metadata: Option<&ReleaseObservation>) -> Status {
    if !live {
        return Status::Warn;
    }
    let Some(meta) = metadata else {
        return Status::Warn;
    };
    if meta.repository_found == Some(false) || !meta.errors.is_empty() {
        return Status::Fail;
    }
    if meta.checksum_verification_passed == Some(false) && meta.checksum_verification_attempted == Some(true) {
        return Status::Fail;
    }
    if meta.signature_verification_passed == Some(false) && meta.signature_verification_attempted == Some(true) {
        return Status::Fail;
    }
    if meta.release_count == Some(0) {
        return Status::Warn;
    }
    if meta.checksum_asset_count == Some(0) || meta.signature_asset_count == Some(0) {
        return Status::Warn;
    }
    if meta.checksum_verification_passed != Some(true) {
        return Status::Warn;
    }
    if meta.signature_verification_passed != Some(true) {
        return Status::Warn;
    }
    Status::Info
}

#[cfg(test)]
mod tests {
    use super::*;

    fn clean_live_meta() -> ReleaseObservation {
        ReleaseObservation {
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
            checksum_verification_attempted: Some(true),
            checksum_verification_passed: Some(true),
            ..ReleaseObservation::default()
        }
    }

    #[test]
    fn offline_is_warn_not_success() {
        assert_eq!(status_for(false, None), Status::Warn);
    }

    #[test]
    fn live_api_errors_fail() {
        let mut meta = clean_live_meta();
        meta.errors.push("api error".to_string());
        assert_eq!(status_for(true, Some(&meta)), Status::Fail);
    }

    #[test]
    fn checksum_failure_fails() {
        let mut meta = clean_live_meta();
        meta.checksum_verification_passed = Some(false);
        assert_eq!(status_for(true, Some(&meta)), Status::Fail);
    }

    #[test]
    fn signature_failure_fails() {
        let mut meta = clean_live_meta();
        meta.signature_verification_passed = Some(false);
        assert_eq!(status_for(true, Some(&meta)), Status::Fail);
    }

    #[test]
    fn missing_signature_warns() {
        let mut meta = clean_live_meta();
        meta.signature_asset_count = Some(0);
        meta.signature_verification_attempted = Some(false);
        meta.signature_verification_passed = None;
        assert_eq!(status_for(true, Some(&meta)), Status::Warn);
    }

    #[test]
    fn checksum_and_signature_pass_is_info() {
        let meta = clean_live_meta();
        assert_eq!(status_for(true, Some(&meta)), Status::Info);
    }
}
EOF

cat > "$SRC/verify/mod.rs" <<'EOF'
use crate::error::VerificationError;
use std::{fs, path::{Path, PathBuf}, process};

pub mod checksum;
pub mod signature;

fn verification_work_dir(prefix: &str, target: &str, tag: &str) -> Result<PathBuf, String> {
    let safe_target = target.replace('/', "_");
    let safe_tag = tag.replace('/', "_");
    let dir = std::env::current_dir()
        .map_err(|err| format!("could not read current dir: {err}"))?
        .join("target")
        .join(format!("wvp-release-{prefix}-{safe_target}-{safe_tag}-{}", process::id()));
    fs::create_dir_all(&dir).map_err(|err| format!("could not create {prefix} dir: {err}"))?;
    Ok(dir)
}

pub(crate) fn select_single_file_by_suffix(dir: &Path, suffix: &str, label: &str) -> Result<PathBuf, VerificationError> {
    let entries = fs::read_dir(dir).map_err(|err| VerificationError::Io(format!("could not read {label} dir: {err}")))?;
    let mut matches: Vec<PathBuf> = entries
        .filter_map(Result::ok)
        .map(|entry| entry.path())
        .filter(|path| path.file_name().and_then(|name| name.to_str()).map(|name| name.ends_with(suffix)).unwrap_or(false))
        .collect();
    matches.sort();
    match matches.len() {
        0 => Err(VerificationError::MissingAsset { suffix: suffix.to_string() }),
        1 => Ok(matches.remove(0)),
        _ => {
            let names = matches.iter().filter_map(|path| path.file_name().and_then(|name| name.to_str())).collect::<Vec<_>>().join(", ");
            Err(VerificationError::AmbiguousAsset { label: label.to_string(), suffix: suffix.to_string(), names })
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn unique_dir(label: &str) -> PathBuf {
        let mut dir = std::env::temp_dir();
        let nanos = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos();
        dir.push(format!("wvp-release-check-{label}-{}-{nanos}", process::id()));
        fs::create_dir_all(&dir).unwrap();
        dir
    }

    #[test]
    fn selects_single_signature_asset() {
        let dir = unique_dir("single-signature");
        let expected = dir.join("release.bin.sig");
        fs::write(&expected, b"sig").unwrap();
        let actual = select_single_file_by_suffix(&dir, ".sig", "signature").unwrap();
        assert_eq!(actual, expected);
        let _ = fs::remove_dir_all(dir);
    }

    #[test]
    fn rejects_missing_signature_asset() {
        let dir = unique_dir("missing-signature");
        let err = select_single_file_by_suffix(&dir, ".sig", "signature").unwrap_err();
        assert!(err.to_string().contains("no .sig asset found"));
        let _ = fs::remove_dir_all(dir);
    }

    #[test]
    fn rejects_multiple_signature_assets() {
        let dir = unique_dir("multiple-signatures");
        fs::write(dir.join("release-a.bin.sig"), b"sig-a").unwrap();
        fs::write(dir.join("release-b.bin.sig"), b"sig-b").unwrap();
        let err = select_single_file_by_suffix(&dir, ".sig", "signature").unwrap_err();
        assert!(err.to_string().contains("multiple signature assets found"));
        let _ = fs::remove_dir_all(dir);
    }

    #[test]
    fn rejects_multiple_checksum_assets() {
        let dir = unique_dir("multiple-checksums");
        fs::write(dir.join("release-a.sha256"), b"a").unwrap();
        fs::write(dir.join("release-b.sha256"), b"b").unwrap();
        let err = select_single_file_by_suffix(&dir, ".sha256", "checksum").unwrap_err();
        assert!(err.to_string().contains("multiple checksum assets found"));
        let _ = fs::remove_dir_all(dir);
    }
}
EOF

cat > "$SRC/verify/checksum.rs" <<'EOF'
use super::{select_single_file_by_suffix, verification_work_dir};
use crate::error::VerificationError;
use std::{fs, process::Command};

pub fn verify_checksum_asset(target: &str, tag: &str) -> (Option<bool>, Option<bool>, Option<String>) {
    match verify_checksum_asset_result(target, tag) {
        Ok(passed) => (Some(true), Some(passed), None),
        Err(err) => (Some(true), Some(false), Some(err.to_string())),
    }
}

fn verify_checksum_asset_result(target: &str, tag: &str) -> Result<bool, VerificationError> {
    let dir = verification_work_dir("checksum", target, tag).map_err(VerificationError::Io)?;
    let result = (|| {
        let output = Command::new("gh")
            .args(["release", "download", tag, "--repo", target, "--dir"])
            .arg(&dir)
            .arg("--clobber")
            .output()
            .map_err(|err| VerificationError::CommandFailed { context: "failed to execute gh release download".to_string(), detail: err.to_string() })?;
        if !output.status.success() {
            return Err(VerificationError::CommandFailed { context: "gh release download failed".to_string(), detail: String::from_utf8_lossy(&output.stderr).trim().to_string() });
        }
        let checksum_file = select_single_file_by_suffix(&dir, ".sha256", "checksum")?;
        let checksum_name = checksum_file.file_name().and_then(|name| name.to_str()).ok_or_else(|| VerificationError::InvalidUtf8Filename("checksum".to_string()))?;
        let output = Command::new("sha256sum")
            .arg("-c")
            .arg(checksum_name)
            .current_dir(&dir)
            .output()
            .map_err(|err| VerificationError::CommandFailed { context: "failed to execute sha256sum".to_string(), detail: err.to_string() })?;
        if output.status.success() {
            Ok(true)
        } else {
            Err(VerificationError::CommandFailed { context: "sha256sum verification failed".to_string(), detail: String::from_utf8_lossy(&output.stderr).trim().to_string() })
        }
    })();
    let _ = fs::remove_dir_all(&dir);
    result
}
EOF

cat > "$SRC/verify/signature.rs" <<'EOF'
use super::{select_single_file_by_suffix, verification_work_dir};
use crate::error::VerificationError;
use std::{fs, path::{Path, PathBuf}, process::Command};

const PUBLIC_VERIFICATION_KEY_PATH: &str = "keys/release/wvp-release-signing-public.pem";

pub fn verify_signature_asset(target: &str, tag: &str) -> (Option<bool>, Option<bool>, Option<String>) {
    let public_key = PathBuf::from(PUBLIC_VERIFICATION_KEY_PATH);
    if !public_key.is_file() {
        return (Some(false), None, Some(VerificationError::MissingPublicKey(PUBLIC_VERIFICATION_KEY_PATH.to_string()).to_string()));
    }
    match verify_signature_asset_result(target, tag, &public_key) {
        Ok(passed) => (Some(true), Some(passed), None),
        Err(err) => (Some(true), Some(false), Some(err.to_string())),
    }
}

fn verify_signature_asset_result(target: &str, tag: &str, public_key: &Path) -> Result<bool, VerificationError> {
    let dir = verification_work_dir("signature", target, tag).map_err(VerificationError::Io)?;
    let result = (|| {
        let output = Command::new("gh")
            .args(["release", "download", tag, "--repo", target, "--dir"])
            .arg(&dir)
            .arg("--clobber")
            .output()
            .map_err(|err| VerificationError::CommandFailed { context: "failed to execute gh release download".to_string(), detail: err.to_string() })?;
        if !output.status.success() {
            return Err(VerificationError::CommandFailed { context: "gh release download failed".to_string(), detail: String::from_utf8_lossy(&output.stderr).trim().to_string() });
        }
        let signature_file = select_single_file_by_suffix(&dir, ".sig", "signature")?;
        let signature_name = signature_file.file_name().and_then(|name| name.to_str()).ok_or_else(|| VerificationError::InvalidUtf8Filename("signature".to_string()))?;
        let signed_asset_name = signature_name.strip_suffix(".sig").ok_or_else(|| VerificationError::MissingSignedAsset(signature_name.to_string()))?;
        let signed_asset = dir.join(signed_asset_name);
        if !signed_asset.is_file() {
            return Err(VerificationError::MissingSignedAsset(signed_asset_name.to_string()));
        }
        verify_detached_signature(public_key, &signature_file, &signed_asset)?;
        Ok(true)
    })();
    let _ = fs::remove_dir_all(&dir);
    result
}

pub(crate) fn verify_detached_signature(public_key: &Path, signature_file: &Path, signed_asset: &Path) -> Result<(), VerificationError> {
    let output = Command::new("openssl")
        .args(["dgst", "-sha256", "-verify"])
        .arg(public_key)
        .arg("-signature")
        .arg(signature_file)
        .arg(signed_asset)
        .output()
        .map_err(|err| VerificationError::CommandFailed { context: "failed to execute openssl".to_string(), detail: err.to_string() })?;
    if output.status.success() {
        return Ok(());
    }
    let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();
    let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
    let detail = if stderr.is_empty() { stdout } else { stderr };
    Err(VerificationError::SignatureVerificationFailed(detail))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::process::{self, Command};

    #[derive(Debug)]
    struct SignatureFixture {
        dir: PathBuf,
        public_key: PathBuf,
        wrong_public_key: PathBuf,
        asset: PathBuf,
        signature: PathBuf,
    }

    fn unique_dir(label: &str) -> PathBuf {
        let mut dir = std::env::temp_dir();
        let nanos = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos();
        dir.push(format!("wvp-release-check-{label}-{}-{nanos}", process::id()));
        fs::create_dir_all(&dir).unwrap();
        dir
    }

    fn run_checked_command(command: &mut Command) {
        let output = command.output().expect("command must execute");
        assert!(output.status.success(), "command failed\nstdout:\n{}\nstderr:\n{}", String::from_utf8_lossy(&output.stdout), String::from_utf8_lossy(&output.stderr));
    }

    fn build_signature_fixture(label: &str) -> SignatureFixture {
        let dir = unique_dir(label);
        let signing_key = dir.join("signing-key.pem");
        let public_key = dir.join("verification-key.pem");
        let wrong_signing_key = dir.join("wrong-signing-key.pem");
        let wrong_public_key = dir.join("wrong-verification-key.pem");
        let asset = dir.join("release.bin");
        let signature = dir.join("release.bin.sig");
        fs::write(&asset, b"original release bytes\n").unwrap();
        run_checked_command(Command::new("openssl").arg("genpkey").arg("-algorithm").arg("RSA").arg("-pkeyopt").arg("rsa_keygen_bits:3072").arg("-out").arg(&signing_key));
        run_checked_command(Command::new("openssl").arg("pkey").arg("-in").arg(&signing_key).arg("-pubout").arg("-out").arg(&public_key));
        run_checked_command(Command::new("openssl").arg("genpkey").arg("-algorithm").arg("RSA").arg("-pkeyopt").arg("rsa_keygen_bits:3072").arg("-out").arg(&wrong_signing_key));
        run_checked_command(Command::new("openssl").arg("pkey").arg("-in").arg(&wrong_signing_key).arg("-pubout").arg("-out").arg(&wrong_public_key));
        run_checked_command(Command::new("openssl").arg("dgst").arg("-sha256").arg("-sign").arg(&signing_key).arg("-out").arg(&signature).arg(&asset));
        SignatureFixture { dir, public_key, wrong_public_key, asset, signature }
    }

    #[test]
    fn signature_verification_accepts_valid_signature() {
        let fixture = build_signature_fixture("valid-signature");
        let result = verify_detached_signature(&fixture.public_key, &fixture.signature, &fixture.asset);
        assert!(result.is_ok());
        let _ = fs::remove_dir_all(fixture.dir);
    }

    #[test]
    fn signature_tamper_rejects_modified_asset() {
        let fixture = build_signature_fixture("tampered-asset");
        fs::write(&fixture.asset, b"tampered release bytes\n").unwrap();
        let result = verify_detached_signature(&fixture.public_key, &fixture.signature, &fixture.asset);
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("signature verification failed"));
        let _ = fs::remove_dir_all(fixture.dir);
    }

    #[test]
    fn signature_tamper_rejects_modified_signature() {
        let fixture = build_signature_fixture("tampered-signature");
        let mut bytes = fs::read(&fixture.signature).unwrap();
        assert!(!bytes.is_empty());
        bytes[0] ^= 0x01;
        fs::write(&fixture.signature, bytes).unwrap();
        let result = verify_detached_signature(&fixture.public_key, &fixture.signature, &fixture.asset);
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("signature verification failed"));
        let _ = fs::remove_dir_all(fixture.dir);
    }

    #[test]
    fn signature_tamper_rejects_wrong_public_key() {
        let fixture = build_signature_fixture("wrong-public-key");
        let result = verify_detached_signature(&fixture.wrong_public_key, &fixture.signature, &fixture.asset);
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("signature verification failed"));
        let _ = fs::remove_dir_all(fixture.dir);
    }
}
EOF

cat > "$SRC/provider.rs" <<'EOF'
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
    let output = Command::new("gh").args(["api", endpoint, "--jq", jq]).output().map_err(|err| format!("failed to execute gh: {err}"))?;
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();
        let message = if stderr.is_empty() { format!("gh api failed for endpoint: {endpoint}") } else { format!("gh api failed for endpoint {endpoint}: {stderr}") };
        return Err(message);
    }
    Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
}

fn gh_count(endpoint: &str, jq: &str) -> Result<usize, String> {
    let value = gh_api(endpoint, jq)?;
    value.parse::<usize>().map_err(|err| VerificationError::CountParse { endpoint: endpoint.to_string(), detail: err.to_string() }).map_err(|err| err.to_string())
}

fn inspect_github(target: &RepositoryTarget) -> ReleaseObservation {
    let target_string = target.to_string();
    let mut errors = Vec::new();

    let repository_found = match gh_api(&format!("repos/{target_string}"), ".full_name") {
        Ok(full_name) => Some(full_name.eq_ignore_ascii_case(&target_string)),
        Err(err) => { errors.push(err); Some(false) }
    };

    let release_count = match gh_count(&format!("repos/{target_string}/releases?per_page=100"), "length") {
        Ok(count) => Some(count),
        Err(err) => { errors.push(err); None }
    };

    let tag_count = match gh_count(&format!("repos/{target_string}/tags?per_page=100"), "length") {
        Ok(count) => Some(count),
        Err(err) => { errors.push(err); None }
    };

    let latest_endpoint = format!("repos/{target_string}/releases?per_page=1");
    let (latest_release_found, latest_release_tag, latest_release_asset_count, checksum_asset_count, signature_asset_count) = match release_count {
        Some(0) => (Some(false), None, Some(0), Some(0), Some(0)),
        Some(_) => {
            let tag = match gh_api(&latest_endpoint, ".[0].tag_name // \"\"") {
                Ok(value) if value.is_empty() => None,
                Ok(value) => Some(value),
                Err(err) => { errors.push(err); None }
            };
            let asset_count = match gh_count(&latest_endpoint, "[.[0].assets[]?] | length") {
                Ok(count) => Some(count),
                Err(err) => { errors.push(err); None }
            };
            let checksum_count = match gh_count(&latest_endpoint, r#"[.[0].assets[]? | select(.name | test("(?i)(sha256|sha512|checksums?|digest)"))] | length"#) {
                Ok(count) => Some(count),
                Err(err) => { errors.push(err); None }
            };
            let signature_count = match gh_count(&latest_endpoint, r#"[.[0].assets[]? | select(.name | test("(?i)(\.(sig|asc|minisig|gpg)$|\.signature$)"))] | length"#) {
                Ok(count) => Some(count),
                Err(err) => { errors.push(err); None }
            };
            (Some(tag.is_some()), tag, asset_count, checksum_count, signature_count)
        }
        None => (None, None, None, None, None),
    };

    let (checksum_verification_attempted, checksum_verification_passed, checksum_verification_error) = match (&latest_release_tag, checksum_asset_count) {
        (Some(tag), Some(count)) if count > 0 => verify_checksum_asset(&target_string, tag),
        (Some(_), Some(0)) => (Some(false), Some(false), Some("no checksum asset found".to_string())),
        _ => (Some(false), None, None),
    };

    let (signature_verification_attempted, signature_verification_passed, signature_verification_error) = match (&latest_release_tag, signature_asset_count) {
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
EOF

cat > "$SRC/report.rs" <<'EOF'
use crate::{classify::Status, model::{Config, ReleaseObservation}, SUMMARY, TOOL_NAME, VERSION};
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

pub fn render_json(cfg: &Config, status: Status, observation: Option<&ReleaseObservation>) -> String {
    let empty = ReleaseObservation::default();
    let meta = observation.unwrap_or(&empty);
    let mut out = String::new();
    let _ = writeln!(out, "{{");
    let _ = writeln!(out, "  \"tool\": {},", json_value(&TOOL_NAME));
    let _ = writeln!(out, "  \"version\": {},", json_value(&VERSION));
    let _ = writeln!(out, "  \"target\": {},", json_value(&cfg.target.to_string()));
    let _ = writeln!(out, "  \"status\": {},", json_value(&status.as_str()));
    let _ = writeln!(out, "  \"classification\": \"observed\",");
    let _ = writeln!(out, "  \"live_inspection\": {},", cfg.live);
    let _ = writeln!(out, "  \"summary\": {},", json_value(&SUMMARY));
    let _ = writeln!(out, "  \"github\": {{");
    json_line(&mut out, "repository_found", &meta.repository_found, true);
    json_line(&mut out, "release_count", &meta.release_count, true);
    json_line(&mut out, "tag_count", &meta.tag_count, true);
    json_line(&mut out, "latest_release_found", &meta.latest_release_found, true);
    json_line(&mut out, "latest_release_tag", &meta.latest_release_tag, true);
    json_line(&mut out, "latest_release_asset_count", &meta.latest_release_asset_count, true);
    json_line(&mut out, "checksum_asset_count", &meta.checksum_asset_count, true);
    json_line(&mut out, "signature_asset_count", &meta.signature_asset_count, true);
    json_line(&mut out, "signature_verification_attempted", &meta.signature_verification_attempted, true);
    json_line(&mut out, "signature_verification_passed", &meta.signature_verification_passed, true);
    json_line(&mut out, "signature_verification_error", &meta.signature_verification_error, true);
    json_line(&mut out, "checksum_verification_attempted", &meta.checksum_verification_attempted, true);
    json_line(&mut out, "checksum_verification_passed", &meta.checksum_verification_passed, true);
    json_line(&mut out, "checksum_verification_error", &meta.checksum_verification_error, true);
    let _ = writeln!(out, "    \"errors\": [");
    for (index, error) in meta.errors.iter().enumerate() {
        let comma = if index + 1 == meta.errors.len() { "" } else { "," };
        let _ = writeln!(out, "      {}{}", json_value(error), comma);
    }
    let _ = writeln!(out, "    ]");
    let _ = writeln!(out, "  }},");
    let _ = writeln!(out, "  \"limitations\": [");
    for (index, limitation) in LIMITATIONS.iter().enumerate() {
        let comma = if index + 1 == LIMITATIONS.len() { "" } else { "," };
        let _ = writeln!(out, "    {}{}", json_value(limitation), comma);
    }
    let _ = writeln!(out, "  ]");
    let _ = writeln!(out, "}}");
    out
}

pub fn render_text(cfg: &Config, status: Status, observation: Option<&ReleaseObservation>) -> String {
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
        let _ = writeln!(out, "latest_release_asset_count: {:?}", meta.latest_release_asset_count);
        let _ = writeln!(out, "checksum_asset_count: {:?}", meta.checksum_asset_count);
        let _ = writeln!(out, "signature_asset_count: {:?}", meta.signature_asset_count);
        let _ = writeln!(out, "signature_verification_attempted: {:?}", meta.signature_verification_attempted);
        let _ = writeln!(out, "signature_verification_passed: {:?}", meta.signature_verification_passed);
        let _ = writeln!(out, "signature_verification_error: {:?}", meta.signature_verification_error);
        let _ = writeln!(out, "checksum_verification_attempted: {:?}", meta.checksum_verification_attempted);
        let _ = writeln!(out, "checksum_verification_passed: {:?}", meta.checksum_verification_passed);
        let _ = writeln!(out, "checksum_verification_error: {:?}", meta.checksum_verification_error);
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
        let cfg = Config { target: RepositoryTarget::parse("nightfall-wizard/wizard-verification-protocol").unwrap(), json: true, live: false };
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
        let cfg = Config { target: RepositoryTarget::parse("owner/repo").unwrap(), json: true, live: true };
        let meta = ReleaseObservation { errors: vec!["quote \" newline\n tab\t slash\\".to_string()], ..ReleaseObservation::default() };
        let out = render_json(&cfg, Status::Fail, Some(&meta));
        let parsed: serde_json::Value = serde_json::from_str(&out).unwrap();
        assert_eq!(parsed["github"]["errors"][0], "quote \" newline\n tab\t slash\\");
    }
}
EOF

cat > "$SRC/lib.rs" <<'EOF'
pub mod classify;
pub mod error;
pub mod model;
pub mod provider;
pub mod report;
pub mod verify;

use classify::status_for;
use model::Config;
use provider::{GhCliProvider, ReleaseEvidenceProvider};

pub const TOOL_NAME: &str = "wvp-release-check";
pub const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const SUMMARY: &str = "GitHub release metadata, artifact discovery, checksum verification and signature verification baseline";

pub fn parse_args(args: &[String]) -> Result<Config, String> {
    let mut target = None;
    let mut json = false;
    let mut live = false;
    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--target" => {
                i += 1;
                let value = args.get(i).ok_or("--target requires owner/repo")?;
                target = Some(model::RepositoryTarget::parse(value)?);
            }
            "--json" => json = true,
            "--live" => live = true,
            "-h" | "--help" => return Err("HELP".to_string()),
            other => return Err(format!("unknown argument: {other}")),
        }
        i += 1;
    }
    Ok(Config { target: target.ok_or("missing --target owner/repo")?, json, live })
}

pub fn print_help() {
    println!("{TOOL_NAME} {VERSION}");
    println!("Usage: {TOOL_NAME} --target owner/repo [--json] [--live]");
    println!("Status: release metadata, artifact discovery and checksum verification baseline; not an audit.");
}

pub fn run(cfg: &Config) {
    let provider = GhCliProvider;
    let observation = if cfg.live { Some(provider.observe(&cfg.target)) } else { None };
    let status = status_for(cfg.live, observation.as_ref());
    if cfg.json {
        print!("{}", report::render_json(cfg, status, observation.as_ref()));
    } else {
        print!("{}", report::render_text(cfg, status, observation.as_ref()));
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_target() {
        let args = vec!["--target".to_string(), "owner/repo".to_string()];
        let cfg = parse_args(&args).unwrap();
        assert_eq!(cfg.target.to_string(), "owner/repo");
        assert!(!cfg.json);
        assert!(!cfg.live);
    }

    #[test]
    fn parses_json_and_live() {
        let args = vec!["--target".to_string(), "owner/repo".to_string(), "--json".to_string(), "--live".to_string()];
        let cfg = parse_args(&args).unwrap();
        assert!(cfg.json);
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
}
EOF

cat > "$SRC/main.rs" <<'EOF'
use std::{env, process};
use wvp_release_check::{parse_args, print_help, run};

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    match parse_args(&args) {
        Ok(cfg) => run(&cfg),
        Err(err) if err == "HELP" => print_help(),
        Err(err) => {
            eprintln!("ERROR: {err}");
            print_help();
            process::exit(2);
        }
    }
}
EOF

cat > docs/architecture/WVP-RELEASE-REALITY-ENGINE.md <<'EOF'
# WVP Release-Reality Engine Architecture

## Purpose

The release-reality engine separates verification policy from live GitHub access and CLI rendering.

The goal is not to make stronger claims. The goal is to make the existing claim boundary easier to review, test, and maintain.

## Boundaries

| Layer | Responsibility | Must not do |
|---|---|---|
| CLI | Parse command-line flags and call the library | Decide trust status |
| Model | Define typed observations and targets | Perform I/O |
| Provider | Collect evidence from GitHub or fixtures | Interpret security meaning |
| Verify | Check checksum and detached signature artifacts | Execute release binaries |
| Classify | Convert observations into INFO/WARN/FAIL | Read network or filesystem |
| Report | Render stable human/JSON output | Change verification meaning |

## Security posture

The engine treats missing evidence as a warning, failed verified evidence as failure, and offline metadata-only output as non-success.

INFO requires both checksum and signature verification to pass.

## Explicit non-claims

This engine does not prove:

- binary safety
- source-to-binary correspondence
- reproducible builds
- external audit status
- legal clearance
- investment quality
- custody safety
EOF

cat > docs/threat-model/WVP-RELEASE-REALITY-THREAT-MODEL.md <<'EOF'
# WVP Release-Reality Threat Model

## Assets protected

- claim boundary integrity
- user interpretation of release evidence
- repository safety expectations
- release artifact verification semantics

## Threats

| Threat | Mitigation |
|---|---|
| Metadata mistaken for security proof | Hard non-claim list remains in output |
| Missing signatures treated as success | Classifier returns WARN |
| Failed checksum treated as warning | Classifier returns FAIL |
| Failed signature treated as warning | Classifier returns FAIL |
| CLI input used as shell command text | Target parser restricts owner/repo shape |
| Release binaries executed during verification | Verification code only hashes/verifies artifacts |
| JSON output injection through errors | Report uses serde_json escaping |

## Non-goals

This is not a cryptographic audit, consensus audit, wallet audit, legal assessment, or investment assessment.
EOF

cat > docs/adr/0001-release-reality-core-boundary.md <<'EOF'
# ADR 0001: Release-Reality Core Boundary

## Status

Accepted for PR review.

## Context

The release checker had useful behavior, tests, and conformance gates, but core policy was less reviewable while concentrated in the executable entrypoint.

## Decision

Move release-reality behavior into a typed Rust library boundary:

- CLI remains thin.
- I/O is isolated behind provider code.
- Classification is pure and testable.
- Reporting is separate from verification logic.
- Checksum and signature verification are separate modules.

## Consequences

Positive:

- smaller review surface
- stronger regression tests
- easier fixture-driven checks
- clearer audit preparation

Tradeoff:

- more files
- slightly more module structure
- dependency on serde/serde_json for safer JSON rendering
EOF

cat > docs/review/WVP-RELEASE-REALITY-REVIEW-CHECKLIST.md <<'EOF'
# WVP Release-Reality Review Checklist

Reviewers should check:

- [ ] `main.rs` is only CLI glue.
- [ ] Live GitHub access is isolated from classification.
- [ ] INFO cannot occur without checksum and signature verification passing.
- [ ] Checksum failure produces FAIL.
- [ ] Signature failure produces FAIL.
- [ ] Missing evidence stays WARN, not INFO.
- [ ] JSON output remains parseable with escaped error strings.
- [ ] No release binary is executed.
- [ ] No seed, private key, token, wallet, custody, or user-funds data is read.
- [ ] No audit, legal, investment, custody, binary-safety, source-to-binary, or reproducible-build claim is added.
- [ ] Existing conformance output remains compatible.
EOF

cargo generate-lockfile
cargo fmt --all
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace --locked

./conformance/release-check-smoke.sh
./conformance/release-check-signature-asset-matching.sh
./conformance/release-check-signature-tamper-negative.sh

git diff --check

git add "$CRATE/Cargo.toml" Cargo.lock "$SRC/main.rs" "$SRC/lib.rs" "$SRC/model.rs" "$SRC/error.rs" "$SRC/classify.rs" "$SRC/provider.rs" "$SRC/report.rs" "$SRC/verify/mod.rs" "$SRC/verify/checksum.rs" "$SRC/verify/signature.rs" docs/architecture/WVP-RELEASE-REALITY-ENGINE.md docs/threat-model/WVP-RELEASE-REALITY-THREAT-MODEL.md docs/adr/0001-release-reality-core-boundary.md docs/review/WVP-RELEASE-REALITY-REVIEW-CHECKLIST.md

git commit -m "refactor: extract release reality core boundary"

cat > .wvp_pr_body.md <<'EOF'
## Summary

Extracts the WVP release-reality checker into a typed Rust library boundary.

## What changed

- keeps `main.rs` as thin CLI glue
- adds typed repository and release observation models
- isolates GitHub CLI collection in provider code
- isolates checksum and detached-signature verification modules
- isolates INFO/WARN/FAIL classification as pure policy logic
- keeps JSON output compatible with existing conformance checks
- adds architecture, threat-model, ADR, and review checklist docs

## Security boundary

This PR does not claim:

- binary safety
- source-to-binary proof
- reproducible-build proof
- external audit status
- legal clearance
- investment quality
- custody safety

## Validation

- `cargo fmt --all`
- `cargo clippy --workspace --all-targets -- -D warnings`
- `cargo test --workspace --locked`
- `./conformance/release-check-smoke.sh`
- `./conformance/release-check-signature-asset-matching.sh`
- `./conformance/release-check-signature-tamper-negative.sh`
- `git diff --check`

## Review focus

Review should focus on whether the new module boundary reduces long-term risk:

1. Does `main.rs` avoid policy decisions?
2. Is live I/O separated from classification?
3. Can INFO appear only when checksum and signature verification pass?
4. Are non-claims preserved?
5. Are adversarial failure cases covered?
EOF

if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  git push -u origin "$BRANCH"
  gh pr create --title "refactor: extract release reality core boundary" --body-file .wvp_pr_body.md --base main --head "$BRANCH" || true
else
  echo
  echo "LOCAL COMMIT COMPLETE."
  echo "Branch: $BRANCH"
  echo "gh is not authenticated or not installed, so no PR was opened."
  echo "To push later: git push -u origin $BRANCH"
fi

echo
echo "DONE: WVP release-reality core refactor branch completed."
