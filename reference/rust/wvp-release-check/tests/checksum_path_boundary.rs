use std::fs;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use wvp_release_check::verify::checksum_boundary::verify_checksum_directory;

static NEXT: AtomicU64 = AtomicU64::new(0);
const DIGEST: &str = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";
struct Fixture(PathBuf);
impl Fixture {
    fn new() -> Self {
        let root = std::env::temp_dir().join(format!(
            "wvp-boundary-{}-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        ));
        fs::create_dir(&root).unwrap();
        fs::create_dir(root.join("assets")).unwrap();
        fs::write(root.join("nightfall-wallet"), b"").unwrap();
        fs::write(root.join("assets/release.bin"), b"").unwrap();
        Self(root)
    }
    fn check(&self, name: &str) -> Result<(), String> {
        self.check_raw(&format!("{DIGEST}  {name}\n"))
    }
    fn check_raw(&self, raw: &str) -> Result<(), String> {
        fs::write(self.0.join("assets/release.sha256"), raw).unwrap();
        verify_checksum_directory(&self.0.join("assets"), "release.sha256")
    }
}
impl Drop for Fixture {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

#[test]
fn valid_control() {
    let f = Fixture::new();
    assert!(f.check("release.bin").is_ok());
    assert!(f.check_raw(&format!("{DIGEST} *release.bin\n")).is_ok());
}

#[test]
fn fixture_traversal_is_rejected() {
    let fixture: serde_json::Value = serde_json::from_str(include_str!(
        "../../../../test-vectors/release-check/negative/FRC-SEC-002-path-traversal.json"
    ))
    .unwrap();
    let name = fixture["artifact"]["name"].as_str().unwrap();
    assert_eq!(name, "../nightfall-wallet");
    // Use the correct hash of the synthetic outside file, so digest mismatch
    // cannot accidentally make the boundary regression pass.
    assert!(
        Fixture::new().check(name).is_err(),
        "outside file was accepted"
    );
}

#[test]
fn absolute_path_is_rejected() {
    let f = Fixture::new();
    assert!(f
        .check(f.0.join("nightfall-wallet").to_str().unwrap())
        .is_err());
}

#[cfg(unix)]
#[test]
fn symlink_escape_is_rejected() {
    let f = Fixture::new();
    std::os::unix::fs::symlink(f.0.join("nightfall-wallet"), f.0.join("assets/link.bin")).unwrap();
    assert!(f.check("link.bin").is_err());
}

#[cfg(unix)]
#[test]
fn manifest_symlink_is_rejected() {
    let f = Fixture::new();
    fs::write(
        f.0.join("outside.sha256"),
        format!("{DIGEST}  release.bin\n"),
    )
    .unwrap();
    std::os::unix::fs::symlink(
        f.0.join("outside.sha256"),
        f.0.join("assets/release.sha256"),
    )
    .unwrap();
    assert!(verify_checksum_directory(&f.0.join("assets"), "release.sha256").is_err());
}

#[test]
fn malformed_duplicate_and_tampered_inputs_are_rejected() {
    let f = Fixture::new();
    for text in [
        String::new(),
        "garbage\n".into(),
        format!("{DIGEST}  release.bin\n{DIGEST}  release.bin\n"),
        format!("{DIGEST}  C:\\outside.bin\n"),
        format!("{DIGEST}  -\n"),
        format!("{DIGEST}  missing.bin\n"),
    ] {
        assert!(f.check_raw(&text).is_err());
    }
    fs::write(f.0.join("assets/release.bin"), b"changed").unwrap();
    assert!(f.check("release.bin").is_err());
}
