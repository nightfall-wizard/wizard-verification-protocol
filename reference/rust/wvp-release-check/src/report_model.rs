use crate::{
    classify::Status,
    model::{Config, ReleaseObservation},
    SUMMARY, TOOL_NAME, VERSION,
};
use serde::Serialize;

pub const REPORT_SCHEMA_VERSION: u32 = 1;

pub const REPORT_LIMITATIONS: [&str; 7] = [
    "not an audit",
    "release metadata is not security proof",
    "asset name discovery is not checksum verification",
    "checksum verification is integrity verification only",
    "signature asset discovery is not signature verification",
    "signature verification depends on configured public key",
    "no reproducible build verification yet",
];

#[derive(Debug, Clone, Serialize, PartialEq, Eq)]
pub struct ReleaseCheckReport {
    pub schema_version: u32,
    pub tool: String,
    pub version: String,
    pub target: String,
    pub status: String,
    pub classification: String,
    pub live_inspection: bool,
    pub summary: String,
    pub github: ReleaseObservation,
    pub limitations: Vec<String>,
}

impl ReleaseCheckReport {
    pub fn from_parts(
        cfg: &Config,
        status: Status,
        observation: Option<&ReleaseObservation>,
    ) -> Self {
        Self {
            schema_version: REPORT_SCHEMA_VERSION,
            tool: TOOL_NAME.to_string(),
            version: VERSION.to_string(),
            target: cfg.target.to_string(),
            status: status.as_str().to_string(),
            classification: "observed".to_string(),
            live_inspection: cfg.live,
            summary: SUMMARY.to_string(),
            github: observation.cloned().unwrap_or_default(),
            limitations: REPORT_LIMITATIONS
                .iter()
                .map(|limitation| (*limitation).to_string())
                .collect(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::model::RepositoryTarget;

    #[test]
    fn typed_report_preserves_contract_identity_fields() {
        let cfg = Config {
            target: RepositoryTarget::parse("owner/repo").expect("valid test target"),
            json: true,
            live: false,
        };

        let report = ReleaseCheckReport::from_parts(&cfg, Status::Warn, None);

        assert_eq!(report.schema_version, REPORT_SCHEMA_VERSION);
        assert_eq!(report.tool, TOOL_NAME);
        assert_eq!(report.version, VERSION);
        assert_eq!(report.target, "owner/repo");
        assert_eq!(report.status, "WARN");
        assert_eq!(report.classification, "observed");
        assert!(!report.live_inspection);
        assert_eq!(report.limitations.len(), REPORT_LIMITATIONS.len());
    }
}
