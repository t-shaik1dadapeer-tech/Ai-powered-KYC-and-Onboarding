const { spawnSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const { AnalyzerError } = require("./errors");

function findEngineRoot() {
  const candidates = [
    path.resolve(__dirname, "../../../engines/intelligence"),
    path.resolve(process.cwd(), "engines/intelligence"),
  ];
  for (const candidate of candidates) {
    if (fs.existsSync(path.join(candidate, "src/intelligence/cli.py"))) {
      return candidate;
    }
  }
  throw new AnalyzerError(
    "Repository intelligence engine not found. Expected engines/intelligence/"
  );
}

function findPython(options = {}) {
  const engineRoot = findEngineRoot();
  const venvPython = path.join(engineRoot, ".venv", "bin", "python3");
  if (fs.existsSync(venvPython)) {
    return venvPython;
  }
  return options.python || "python3";
}

function generateReport(repoPath, outputDir, options = {}) {
  const engineRoot = findEngineRoot();
  const python = findPython(options);
  const resolvedOutput = path.resolve(outputDir);

  const args = [
    "-m",
    "intelligence.cli",
    repoPath,
    "-o",
    resolvedOutput,
    "--json",
  ];

  const result = spawnSync(python, args, {
    cwd: engineRoot,
    env: { ...process.env, PYTHONPATH: "src" },
    encoding: "utf-8",
  });

  if (result.error) {
    throw new AnalyzerError(`Failed to run analyzer: ${result.error.message}`);
  }

  if (result.status !== 0) {
    throw new AnalyzerError(
      result.stderr || result.stdout || "Analyzer exited with error",
      result.status
    );
  }

  let summary = null;
  const stdout = result.stdout || "";
  const jsonStart = stdout.indexOf("{");
  const jsonEnd = stdout.lastIndexOf("}");
  if (jsonStart >= 0 && jsonEnd > jsonStart) {
    try {
      summary = JSON.parse(stdout.slice(jsonStart, jsonEnd + 1));
    } catch {
      summary = { raw: stdout };
    }
  }

  return {
    outputDir: resolvedOutput,
    summary,
    stdout: result.stdout,
  };
}

module.exports = { generateReport, findEngineRoot, findPython };
