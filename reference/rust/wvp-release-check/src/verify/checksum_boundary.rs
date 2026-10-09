//! Offline checksum verification for flat release asset directories.
use std::collections::HashSet;
use std::fs::{self, File};
use std::io::Read;
use std::path::Path;
use std::process::{Command, Stdio};

fn valid_name(name: &str) -> bool {
    !name.is_empty()
        && name != "."
        && name != ".."
        && name != "-"
        && !name
            .chars()
            .any(|c| c == '/' || c == '\\' || c == ':' || c.is_control())
}

fn regular_file(path: &Path) -> Result<File, String> {
    let before = fs::symlink_metadata(path).map_err(|e| e.to_string())?;
    if !before.file_type().is_file() {
        return Err("checksum input must be a regular non-symlink file".into());
    }
    let mut options = fs::OpenOptions::new();
    options.read(true);
    #[cfg(any(target_os = "linux", target_os = "android"))]
    {
        use std::os::unix::fs::OpenOptionsExt;
        // Linux/Android O_NOFOLLOW | O_NONBLOCK: reject link swaps and avoid FIFO hangs.
        options.custom_flags(0x20000 | 0x800);
    }
    let file = options.open(path).map_err(|e| e.to_string())?;
    let after = file.metadata().map_err(|e| e.to_string())?;
    if !after.is_file() {
        return Err("checksum input is not a regular file".into());
    }
    #[cfg(unix)]
    {
        use std::os::unix::fs::MetadataExt;
        if before.dev() != after.dev() || before.ino() != after.ino() {
            return Err("checksum input changed while opening".into());
        }
    }
    Ok(file)
}

/// Accept GNU SHA256 text/binary records with flat filenames only.
/// The directory and its ancestors must be controlled by the caller.
pub fn verify_checksum_directory(dir: &Path, manifest: &str) -> Result<(), String> {
    if !valid_name(manifest) {
        return Err("invalid checksum manifest name".into());
    }
    let file = regular_file(&dir.join(manifest))?;
    let mut raw = Vec::new();
    file.take(1_048_577)
        .read_to_end(&mut raw)
        .map_err(|e| e.to_string())?;
    if raw.len() > 1_048_576 {
        return Err("checksum manifest exceeds 1 MiB".into());
    }
    let text = std::str::from_utf8(&raw).map_err(|e| e.to_string())?;
    let mut entries = Vec::new();
    let mut seen = HashSet::new();
    for line in text.lines() {
        let bytes = line.as_bytes();
        if bytes.len() < 67
            || !bytes[..64].iter().all(u8::is_ascii_hexdigit)
            || bytes[64] != b' '
            || !matches!(bytes[65], b' ' | b'*')
        {
            return Err("malformed SHA256 record".into());
        }
        let digest = &line[..64];
        let name = &line[66..];
        if !valid_name(name) {
            return Err("artifact path escapes the flat release boundary".into());
        }
        if name == manifest || !seen.insert(name) {
            return Err("duplicate or self-referencing checksum record".into());
        }
        entries.push((digest, name));
    }
    if entries.is_empty() {
        return Err("empty checksum manifest".into());
    }
    for (digest, name) in entries {
        let file = regular_file(&dir.join(name))?;
        // Pass the opened file, never an untrusted manifest or filename, to sha256sum.
        let output = Command::new("sha256sum")
            .stdin(Stdio::from(file))
            .output()
            .map_err(|e| e.to_string())?;
        let stdout = std::str::from_utf8(&output.stdout).map_err(|e| e.to_string())?;
        let actual = stdout
            .split_whitespace()
            .next()
            .ok_or("missing SHA256 output")?;
        if !output.status.success() || !actual.eq_ignore_ascii_case(digest) {
            return Err("SHA256 mismatch or hash command failure".into());
        }
    }
    Ok(())
}
