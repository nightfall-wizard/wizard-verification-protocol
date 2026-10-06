use crate::error::VerificationError;
use std::{
    fs,
    path::{Path, PathBuf},
    process,
};

pub mod checksum;
pub mod signature;

fn verification_work_dir(prefix: &str, target: &str, tag: &str) -> Result<PathBuf, String> {
    let safe_target = target.replace('/', "_");
    let safe_tag = tag.replace('/', "_");
    let dir = std::env::current_dir()
        .map_err(|err| format!("could not read current dir: {err}"))?
        .join("target")
        .join(format!(
            "wvp-release-{prefix}-{safe_target}-{safe_tag}-{}",
            process::id()
        ));
    fs::create_dir_all(&dir).map_err(|err| format!("could not create {prefix} dir: {err}"))?;
    Ok(dir)
}

pub(crate) fn select_single_file_by_suffix(
    dir: &Path,
    suffix: &str,
    label: &str,
) -> Result<PathBuf, VerificationError> {
    let entries = fs::read_dir(dir)
        .map_err(|err| VerificationError::Io(format!("could not read {label} dir: {err}")))?;
    let mut matches: Vec<PathBuf> = entries
        .filter_map(Result::ok)
        .map(|entry| entry.path())
        .filter(|path| {
            path.file_name()
                .and_then(|name| name.to_str())
                .map(|name| name.ends_with(suffix))
                .unwrap_or(false)
        })
        .collect();
    matches.sort();
    match matches.len() {
        0 => Err(VerificationError::MissingAsset {
            suffix: suffix.to_string(),
        }),
        1 => Ok(matches.remove(0)),
        _ => {
            let names = matches
                .iter()
                .filter_map(|path| path.file_name().and_then(|name| name.to_str()))
                .collect::<Vec<_>>()
                .join(", ");
            Err(VerificationError::AmbiguousAsset {
                label: label.to_string(),
                suffix: suffix.to_string(),
                names,
            })
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

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
