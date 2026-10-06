pub mod classify;
pub mod error;
pub mod model;
pub mod provider;
pub mod report;
pub mod report_model;
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
    Ok(Config {
        target: target.ok_or("missing --target owner/repo")?,
        json,
        live,
    })
}

pub fn print_help() {
    println!("{TOOL_NAME} {VERSION}");
    println!("Usage: {TOOL_NAME} --target owner/repo [--json] [--live]");
    println!("Status: release metadata, artifact discovery and checksum verification baseline; not an audit.");
}

pub fn run(cfg: &Config) {
    let provider = GhCliProvider;
    let observation = if cfg.live {
        Some(provider.observe(&cfg.target))
    } else {
        None
    };
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
        let args = vec![
            "--target".to_string(),
            "owner/repo".to_string(),
            "--json".to_string(),
            "--live".to_string(),
        ];
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
