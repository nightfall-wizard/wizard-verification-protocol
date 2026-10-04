use std::{env, process};

const VERSION: &str = env!("CARGO_PKG_VERSION");

#[derive(Debug, Clone, PartialEq, Eq)]
struct Config {
    target: String,
    json: bool,
}

fn parse_args(args: &[String]) -> Result<Config, String> {
    let mut target: Option<String> = None;
    let mut json = false;
    let mut i = 0;

    while i < args.len() {
        match args[i].as_str() {
            "--target" => {
                i += 1;
                let value = args.get(i).ok_or("--target requires owner/repo")?;
                if !value.contains('/') {
                    return Err("target must use owner/repo form".to_string());
                }
                target = Some(value.clone());
            }
            "--json" => json = true,
            "-h" | "--help" => return Err("HELP".to_string()),
            other => return Err(format!("unknown argument: {other}")),
        }
        i += 1;
    }

    Ok(Config {
        target: target.ok_or("missing --target owner/repo")?,
        json,
    })
}

fn print_help() {
    println!("wvp-release-check {VERSION}");
    println!("Usage: wvp-release-check --target owner/repo [--json]");
    println!("Status: bootstrap implementation; not an audit.");
}

fn print_report(cfg: &Config) {
    if cfg.json {
        println!("{{");
        println!("  \"tool\": \"wvp-release-check\",");
        println!("  \"version\": \"{VERSION}\",");
        println!("  \"target\": \"{}\",", cfg.target);
        println!("  \"status\": \"WARN\",");
        println!("  \"classification\": \"observed\",");
        println!(
            "  \"summary\": \"bootstrap only; live release verification not implemented yet\","
        );
        println!("  \"limitations\": [");
        println!("    \"not an audit\",");
        println!("    \"no signature verification yet\",");
        println!("    \"no checksum verification yet\",");
        println!("    \"no reproducible build verification yet\"");
        println!("  ]");
        println!("}}");
    } else {
        println!("WVP Release Integrity Report");
        println!("tool: wvp-release-check");
        println!("version: {VERSION}");
        println!("target: {}", cfg.target);
        println!("status: WARN");
        println!("classification: observed");
        println!("summary: bootstrap only; live release verification not implemented yet");
        println!("limitation: not an audit");
        println!("limitation: no signature verification yet");
        println!("limitation: no checksum verification yet");
        println!("limitation: no reproducible build verification yet");
    }
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();

    match parse_args(&args) {
        Ok(cfg) => print_report(&cfg),
        Err(err) if err == "HELP" => print_help(),
        Err(err) => {
            eprintln!("ERROR: {err}");
            print_help();
            process::exit(2);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_target() {
        let args = vec!["--target".to_string(), "owner/repo".to_string()];
        let cfg = parse_args(&args).unwrap();
        assert_eq!(cfg.target, "owner/repo");
        assert!(!cfg.json);
    }

    #[test]
    fn parses_json() {
        let args = vec![
            "--target".to_string(),
            "owner/repo".to_string(),
            "--json".to_string(),
        ];
        let cfg = parse_args(&args).unwrap();
        assert!(cfg.json);
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
