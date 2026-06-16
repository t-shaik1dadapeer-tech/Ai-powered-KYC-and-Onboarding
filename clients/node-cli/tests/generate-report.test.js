const { describe, it } = require("node:test");
const assert = require("node:assert/strict");
const path = require("path");
const { generateReportCommand } = require("../commands/generate-report");

const ONBOARDING_API = path.resolve(__dirname, "../../../services/onboarding-api");

describe("generate-report command", () => {
  it("runs intelligence analyzer on onboarding-api", async () => {
    const outputDir = path.join(__dirname, "../.test-output");
    const result = await generateReportCommand({
      path: ONBOARDING_API,
      output: outputDir,
      python: "python3",
    });

    assert.ok(result.summary);
    assert.equal(result.summary.framework, "fastapi");
    assert.ok(result.summary.apis >= 7);
    assert.ok(result.outputDir.includes(".test-output"));
  });
});
