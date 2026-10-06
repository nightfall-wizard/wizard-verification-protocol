use super::{select_single_file_by_suffix, verification_work_dir};
use crate::error::VerificationError;
use std::{
    fs,
    path::{Path, PathBuf},
    process::Command,
};

const PUBLIC_VERIFICATION_KEY_PATH: &str = "keys/release/wvp-release-signing-public.pem";

pub fn verify_signature_asset(
    target: &str,
    tag: &str,
) -> (Option<bool>, Option<bool>, Option<String>) {
    let public_key = PathBuf::from(PUBLIC_VERIFICATION_KEY_PATH);
    if !public_key.is_file() {
        return (
            Some(false),
            None,
            Some(
                VerificationError::MissingPublicKey(PUBLIC_VERIFICATION_KEY_PATH.to_string())
                    .to_string(),
            ),
        );
    }
    match verify_signature_asset_result(target, tag, &public_key) {
        Ok(passed) => (Some(true), Some(passed), None),
        Err(err) => (Some(true), Some(false), Some(err.to_string())),
    }
}

fn verify_signature_asset_result(
    target: &str,
    tag: &str,
    public_key: &Path,
) -> Result<bool, VerificationError> {
    let dir = verification_work_dir("signature", target, tag).map_err(VerificationError::Io)?;
    let result = (|| {
        let output = Command::new("gh")
            .args(["release", "download", tag, "--repo", target, "--dir"])
            .arg(&dir)
            .arg("--clobber")
            .output()
            .map_err(|err| VerificationError::CommandFailed {
                context: "failed to execute gh release download".to_string(),
                detail: err.to_string(),
            })?;
        if !output.status.success() {
            return Err(VerificationError::CommandFailed {
                context: "gh release download failed".to_string(),
                detail: String::from_utf8_lossy(&output.stderr).trim().to_string(),
            });
        }
        let signature_file = select_single_file_by_suffix(&dir, ".sig", "signature")?;
        let signature_name = signature_file
            .file_name()
            .and_then(|name| name.to_str())
            .ok_or_else(|| VerificationError::InvalidUtf8Filename("signature".to_string()))?;
        let signed_asset_name = signature_name
            .strip_suffix(".sig")
            .ok_or_else(|| VerificationError::MissingSignedAsset(signature_name.to_string()))?;
        let signed_asset = dir.join(signed_asset_name);
        if !signed_asset.is_file() {
            return Err(VerificationError::MissingSignedAsset(
                signed_asset_name.to_string(),
            ));
        }
        verify_detached_signature(public_key, &signature_file, &signed_asset)?;
        Ok(true)
    })();
    let _ = fs::remove_dir_all(&dir);
    result
}

pub(crate) fn verify_detached_signature(
    public_key: &Path,
    signature_file: &Path,
    signed_asset: &Path,
) -> Result<(), VerificationError> {
    let output = Command::new("openssl")
        .args(["dgst", "-sha256", "-verify"])
        .arg(public_key)
        .arg("-signature")
        .arg(signature_file)
        .arg(signed_asset)
        .output()
        .map_err(|err| VerificationError::CommandFailed {
            context: "failed to execute openssl".to_string(),
            detail: err.to_string(),
        })?;
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
        let nanos = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        dir.push(format!(
            "wvp-release-check-{label}-{}-{nanos}",
            process::id()
        ));
        fs::create_dir_all(&dir).unwrap();
        dir
    }

    fn run_checked_command(command: &mut Command) {
        let output = command.output().expect("command must execute");
        assert!(
            output.status.success(),
            "command failed\nstdout:\n{}\nstderr:\n{}",
            String::from_utf8_lossy(&output.stdout),
            String::from_utf8_lossy(&output.stderr)
        );
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
        run_checked_command(
            Command::new("openssl")
                .arg("genpkey")
                .arg("-algorithm")
                .arg("RSA")
                .arg("-pkeyopt")
                .arg("rsa_keygen_bits:3072")
                .arg("-out")
                .arg(&signing_key),
        );
        run_checked_command(
            Command::new("openssl")
                .arg("pkey")
                .arg("-in")
                .arg(&signing_key)
                .arg("-pubout")
                .arg("-out")
                .arg(&public_key),
        );
        run_checked_command(
            Command::new("openssl")
                .arg("genpkey")
                .arg("-algorithm")
                .arg("RSA")
                .arg("-pkeyopt")
                .arg("rsa_keygen_bits:3072")
                .arg("-out")
                .arg(&wrong_signing_key),
        );
        run_checked_command(
            Command::new("openssl")
                .arg("pkey")
                .arg("-in")
                .arg(&wrong_signing_key)
                .arg("-pubout")
                .arg("-out")
                .arg(&wrong_public_key),
        );
        run_checked_command(
            Command::new("openssl")
                .arg("dgst")
                .arg("-sha256")
                .arg("-sign")
                .arg(&signing_key)
                .arg("-out")
                .arg(&signature)
                .arg(&asset),
        );
        SignatureFixture {
            dir,
            public_key,
            wrong_public_key,
            asset,
            signature,
        }
    }

    #[test]
    fn signature_verification_accepts_valid_signature() {
        let fixture = build_signature_fixture("valid-signature");
        let result =
            verify_detached_signature(&fixture.public_key, &fixture.signature, &fixture.asset);
        assert!(result.is_ok());
        let _ = fs::remove_dir_all(fixture.dir);
    }

    #[test]
    fn signature_tamper_rejects_modified_asset() {
        let fixture = build_signature_fixture("tampered-asset");
        fs::write(&fixture.asset, b"tampered release bytes\n").unwrap();
        let result =
            verify_detached_signature(&fixture.public_key, &fixture.signature, &fixture.asset);
        assert!(result.is_err());
        assert!(result
            .unwrap_err()
            .to_string()
            .contains("signature verification failed"));
        let _ = fs::remove_dir_all(fixture.dir);
    }

    #[test]
    fn signature_tamper_rejects_modified_signature() {
        let fixture = build_signature_fixture("tampered-signature");
        let mut bytes = fs::read(&fixture.signature).unwrap();
        assert!(!bytes.is_empty());
        bytes[0] ^= 0x01;
        fs::write(&fixture.signature, bytes).unwrap();
        let result =
            verify_detached_signature(&fixture.public_key, &fixture.signature, &fixture.asset);
        assert!(result.is_err());
        assert!(result
            .unwrap_err()
            .to_string()
            .contains("signature verification failed"));
        let _ = fs::remove_dir_all(fixture.dir);
    }

    #[test]
    fn signature_tamper_rejects_wrong_public_key() {
        let fixture = build_signature_fixture("wrong-public-key");
        let result = verify_detached_signature(
            &fixture.wrong_public_key,
            &fixture.signature,
            &fixture.asset,
        );
        assert!(result.is_err());
        assert!(result
            .unwrap_err()
            .to_string()
            .contains("signature verification failed"));
        let _ = fs::remove_dir_all(fixture.dir);
    }
}
