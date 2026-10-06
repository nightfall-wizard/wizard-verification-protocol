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

    if !meta.errors.is_empty() {
        return Status::Fail;
    }

    if meta.repository_found == Some(false) {
        return Status::Fail;
    }

    if meta.repository_found != Some(true) {
        return Status::Warn;
    }

    if !matches!(meta.release_count, Some(count) if count > 0) {
        return Status::Warn;
    }

    if meta.latest_release_found != Some(true) {
        return Status::Warn;
    }

    if meta
        .latest_release_tag
        .as_deref()
        .map(str::is_empty)
        .unwrap_or(true)
    {
        return Status::Warn;
    }

    if meta.checksum_verification_passed == Some(false)
        && meta.checksum_verification_attempted == Some(true)
    {
        return Status::Fail;
    }

    if meta.signature_verification_passed == Some(false)
        && meta.signature_verification_attempted == Some(true)
    {
        return Status::Fail;
    }

    if meta.checksum_asset_count != Some(1) {
        return Status::Warn;
    }

    if meta.signature_asset_count != Some(1) {
        return Status::Warn;
    }

    if meta.checksum_verification_attempted != Some(true) {
        return Status::Warn;
    }

    if meta.signature_verification_attempted != Some(true) {
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
    fn status_fails_when_signature_verification_fails() {
        let mut meta = clean_live_meta();
        meta.signature_verification_passed = Some(false);
        assert_eq!(status_for(true, Some(&meta)), Status::Fail);
    }

    #[test]
    fn status_warns_when_signature_asset_exists_but_not_verified() {
        let mut meta = clean_live_meta();
        meta.signature_asset_count = Some(0);
        meta.signature_verification_attempted = Some(false);
        meta.signature_verification_passed = None;
        assert_eq!(status_for(true, Some(&meta)), Status::Warn);
    }

    #[test]
    fn status_info_when_checksum_and_signature_verification_pass() {
        let meta = clean_live_meta();
        assert_eq!(status_for(true, Some(&meta)), Status::Info);
    }
}
