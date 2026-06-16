const path = require("path");
const { generateReport } = require("../lib/analyzer-client");
const { validateRepoPath } = require("../lib/validators");

async function generateReportCommand(options) {
  const repoPath = validateRepoPath(options.path);
  const outputDir = path.resolve(options.output);

  const result = generateReport(repoPath, outputDir, { python: options.python });

  return {
    outputDir: result.outputDir,
    summary: result.summary,
  };
}

module.exports = { generateReportCommand };
