use std::{env, process};
use wvp_release_check::{parse_args, print_help, run};

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    match parse_args(&args) {
        Ok(cfg) => run(&cfg),
        Err(err) if err == "HELP" => print_help(),
        Err(err) => {
            eprintln!("ERROR: {err}");
            print_help();
            process::exit(2);
        }
    }
}
