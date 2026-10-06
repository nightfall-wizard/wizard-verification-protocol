use proptest::prelude::*;
use wvp_release_check::{
    classify::{status_for, Status},
    model::ReleaseObservation,
};

fn complete_positive_observation() -> ReleaseObservation {
    ReleaseObservation {
        repository_found: Some(true),
        release_count: Some(1),
        tag_count: Some(1),
        latest_release_found: Some(true),
        latest_release_tag: Some("v0.3.0".to_string()),
        latest_release_asset_count: Some(3),
        checksum_asset_count: Some(1),
        signature_asset_count: Some(1),
        checksum_verification_attempted: Some(true),
        checksum_verification_passed: Some(true),
        signature_verification_attempted: Some(true),
        signature_verification_passed: Some(true),
        errors: Vec::new(),
        ..ReleaseObservation::default()
    }
}

fn optional_bool() -> impl Strategy<Value = Option<bool>> {
    prop_oneof![Just(None), Just(Some(false)), Just(Some(true))]
}

fn optional_count() -> impl Strategy<Value = Option<usize>> {
    prop_oneof![
        Just(None),
        Just(Some(0)),
        Just(Some(1)),
        Just(Some(2)),
        Just(Some(usize::MAX)),
    ]
}

#[test]
fn adversarial_complete_positive_evidence_can_reach_info() {
    let meta = complete_positive_observation();
    assert_eq!(status_for(true, Some(&meta)), Status::Info);
}

#[test]
fn adversarial_offline_mode_never_reaches_info() {
    let meta = complete_positive_observation();
    assert_ne!(status_for(false, Some(&meta)), Status::Info);
    assert_ne!(status_for(false, None), Status::Info);
}

#[test]
fn adversarial_duplicate_release_assets_never_reach_info() {
    let mut duplicate_checksum = complete_positive_observation();
    duplicate_checksum.checksum_asset_count = Some(2);
    assert_ne!(status_for(true, Some(&duplicate_checksum)), Status::Info);

    let mut duplicate_signature = complete_positive_observation();
    duplicate_signature.signature_asset_count = Some(2);
    assert_ne!(status_for(true, Some(&duplicate_signature)), Status::Info);
}

#[test]
fn adversarial_missing_positive_metadata_never_reaches_info() {
    let mut missing_repo = complete_positive_observation();
    missing_repo.repository_found = None;
    assert_ne!(status_for(true, Some(&missing_repo)), Status::Info);

    let mut missing_release_count = complete_positive_observation();
    missing_release_count.release_count = None;
    assert_ne!(status_for(true, Some(&missing_release_count)), Status::Info);

    let mut missing_latest_release = complete_positive_observation();
    missing_latest_release.latest_release_found = None;
    assert_ne!(
        status_for(true, Some(&missing_latest_release)),
        Status::Info
    );

    let mut missing_tag = complete_positive_observation();
    missing_tag.latest_release_tag = None;
    assert_ne!(status_for(true, Some(&missing_tag)), Status::Info);

    let mut empty_tag = complete_positive_observation();
    empty_tag.latest_release_tag = Some(String::new());
    assert_ne!(status_for(true, Some(&empty_tag)), Status::Info);
}

#[test]
fn adversarial_failed_verification_remains_fail() {
    let mut checksum_failed = complete_positive_observation();
    checksum_failed.checksum_verification_passed = Some(false);
    assert_eq!(status_for(true, Some(&checksum_failed)), Status::Fail);

    let mut signature_failed = complete_positive_observation();
    signature_failed.signature_verification_passed = Some(false);
    assert_eq!(status_for(true, Some(&signature_failed)), Status::Fail);
}

#[test]
fn adversarial_errors_fail_closed() {
    let mut meta = complete_positive_observation();
    meta.errors.push("synthetic provider error".to_string());
    assert_eq!(status_for(true, Some(&meta)), Status::Fail);
}

proptest! {
    #[test]
    fn adversarial_info_requires_complete_positive_evidence(
        live in any::<bool>(),
        repository_found in optional_bool(),
        release_count in optional_count(),
        latest_release_found in optional_bool(),
        checksum_asset_count in optional_count(),
        signature_asset_count in optional_count(),
        checksum_attempted in optional_bool(),
        checksum_passed in optional_bool(),
        signature_attempted in optional_bool(),
        signature_passed in optional_bool(),
        error_count in 0usize..3,
    ) {
        let mut errors = Vec::new();
        for idx in 0..error_count {
            errors.push(format!("synthetic adversarial error {idx}"));
        }

        let meta = ReleaseObservation {
            repository_found,
            release_count,
            tag_count: Some(1),
            latest_release_found,
            latest_release_tag: latest_release_found
                .filter(|found| *found)
                .map(|_| "v-adversarial".to_string()),
            latest_release_asset_count: Some(3),
            checksum_asset_count,
            signature_asset_count,
            checksum_verification_attempted: checksum_attempted,
            checksum_verification_passed: checksum_passed,
            signature_verification_attempted: signature_attempted,
            signature_verification_passed: signature_passed,
            errors,
            ..ReleaseObservation::default()
        };

        let status = status_for(live, Some(&meta));

        if status == Status::Info {
            prop_assert!(live);
            prop_assert_eq!(meta.repository_found, Some(true));
            prop_assert!(matches!(meta.release_count, Some(count) if count > 0));
            prop_assert_eq!(meta.latest_release_found, Some(true));
            prop_assert!(matches!(meta.latest_release_tag.as_deref(), Some(tag) if !tag.is_empty()));
            prop_assert_eq!(meta.checksum_asset_count, Some(1));
            prop_assert_eq!(meta.signature_asset_count, Some(1));
            prop_assert_eq!(meta.checksum_verification_attempted, Some(true));
            prop_assert_eq!(meta.checksum_verification_passed, Some(true));
            prop_assert_eq!(meta.signature_verification_attempted, Some(true));
            prop_assert_eq!(meta.signature_verification_passed, Some(true));
            prop_assert!(meta.errors.is_empty());
        }
    }
}
