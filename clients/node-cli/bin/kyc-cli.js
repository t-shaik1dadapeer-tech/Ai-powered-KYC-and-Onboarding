#!/usr/bin/env node

const { Command } = require("commander");
const { customerCreate } = require("../commands/customer-create");
const { submitKyc } = require("../commands/submit-kyc");
const { generateReportCommand } = require("../commands/generate-report");
const { CliError } = require("../lib/errors");

const program = new Command();

program
  .name("kyc-cli")
  .description("KYC onboarding and repository intelligence CLI")
  .version("0.1.0");

program
  .command("customer-create")
  .description("Create a new customer")
  .requiredOption("--name <name>", "Customer full name")
  .requiredOption("--email <email>", "Customer email")
  .requiredOption("--phone <phone>", "Customer phone")
  .option("--api-url <url>", "Onboarding API base URL", process.env.API_BASE_URL || "http://localhost:8000")
  .action(async (options) => {
    try {
      const result = await customerCreate(options);
      console.log(JSON.stringify({ ok: true, ...result }, null, 2));
    } catch (err) {
      handleError(err);
    }
  });

program
  .command("submit-kyc")
  .description("Submit KYC for a customer")
  .requiredOption("--customer-id <uuid>", "Customer UUID")
  .requiredOption("--pan <pan>", "PAN number")
  .requiredOption("--account <number>", "Bank account number")
  .requiredOption("--ifsc <ifsc>", "Bank IFSC code")
  .option("--api-url <url>", "Onboarding API base URL", process.env.API_BASE_URL || "http://localhost:8000")
  .action(async (options) => {
    try {
      const result = await submitKyc(options);
      console.log(JSON.stringify({ ok: true, ...result }, null, 2));
    } catch (err) {
      handleError(err);
    }
  });

program
  .command("generate-report")
  .description("Analyze a repository and generate intelligence reports")
  .requiredOption("--path <dir>", "Repository path to analyze")
  .option("--output <dir>", "Output directory for reports", "reports")
  .option("--python <bin>", "Python executable", "python3")
  .action(async (options) => {
    try {
      const result = await generateReportCommand(options);
      console.log(JSON.stringify({ ok: true, ...result }, null, 2));
    } catch (err) {
      handleError(err);
    }
  });

function handleError(err) {
  if (err instanceof CliError) {
    const payload = { ok: false, error: err.code, message: err.message };
    if (err.statusCode) payload.statusCode = err.statusCode;
    console.error(JSON.stringify(payload, null, 2));
    process.exit(1);
  }
  console.error(JSON.stringify({ ok: false, error: "unexpected", message: err.message }, null, 2));
  process.exit(1);
}

program.parse();
