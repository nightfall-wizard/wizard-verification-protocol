use super::{select_single_file_by_suffix, verification_work_dir};
use crate::error::VerificationError;
use std::{fs, process::Command};

pub fn verify_checksum_asset(
    target: &str,
    tag: &str,
) -> (Option<bool>, Option<bool>, Option<String>) {
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
        let checksum_file = select_single_file_by_suffix(&dir, ".sha256", "checksum")?;
        let checksum_name = checksum_file
            .file_name()
            .and_then(|name| name.to_str())
            .ok_or_else(|| VerificationError::InvalidUtf8Filename("checksum".to_string()))?;
        let output = Command::new("sha256sum")
            .arg("-c")
            .arg(checksum_name)
            .current_dir(&dir)
            .output()
            .map_err(|err| VerificationError::CommandFailed {
                context: "failed to execute sha256sum".to_string(),
                detail: err.to_string(),
            })?;
        if output.status.success() {
            Ok(true)
        } else {
            Err(VerificationError::CommandFailed {
                context: "sha256sum verification failed".to_string(),
                detail: String::from_utf8_lossy(&output.stderr).trim().to_string(),
            })
        }
    })();
    let _ = fs::remove_dir_all(&dir);
    result
}
