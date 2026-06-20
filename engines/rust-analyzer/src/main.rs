use std::path::PathBuf;
use std::process;

use clap::{Parser, Subcommand};

use rust_analyzer::scan_repository;

#[derive(Parser)]
#[command(
    name = "rust-analyzer",
    about = "Repository parser and risk calculator"
)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Scan a repository and output JSON analysis
    Scan {
        /// Repository root path
        #[arg(long)]
        path: PathBuf,
        /// Pretty-print JSON
        #[arg(long, default_value_t = true)]
        pretty: bool,
    },
    /// Calculate risk score only
    Risk {
        #[arg(long)]
        path: PathBuf,
    },
}

fn main() {
    if let Err(err) = run() {
        eprintln!(
            "{}",
            serde_json::json!({
                "ok": false,
                "error": err.to_string()
            })
        );
        process::exit(1);
    }
}

fn run() -> rust_analyzer::Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Scan { path, pretty } => {
            let result = scan_repository(&path)?;
            let json = if pretty {
                serde_json::to_string_pretty(&result)?
            } else {
                serde_json::to_string(&result)?
            };
            println!("{json}");
        }
        Commands::Risk { path } => {
            let result = scan_repository(&path)?;
            println!("{}", serde_json::to_string_pretty(&result.risk)?);
        }
    }

    Ok(())
}
