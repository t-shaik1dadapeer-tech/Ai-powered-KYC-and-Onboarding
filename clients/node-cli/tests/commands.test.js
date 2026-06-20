const { describe, it, mock } = require("node:test");
const assert = require("node:assert/strict");
const { customerCreate } = require("../commands/customer-create");
const { submitKyc } = require("../commands/submit-kyc");
const { ValidationError } = require("../lib/errors");

describe("commands", () => {
  it("customer-create validates before API call", async () => {
    await assert.rejects(
      () =>
        customerCreate({
          name: "J",
          email: "bad",
          phone: "123",
          apiUrl: "http://localhost:8000",
        }),
      ValidationError
    );
  });

  it("customer-create calls API with validated payload", async () => {
    const originalFetch = global.fetch;
    global.fetch = mock.fn(async () => ({
      ok: true,
      status: 201,
      text: async () =>
        JSON.stringify({
          id: "550e8400-e29b-41d4-a716-446655440000",
          status: "pending",
          email: "jane@example.com",
        }),
    }));

    try {
      const result = await customerCreate({
        name: "Jane Doe",
        email: "jane@example.com",
        phone: "9876543210",
        apiUrl: "http://localhost:8000",
      });
      assert.equal(result.customerId, "550e8400-e29b-41d4-a716-446655440000");
    } finally {
      global.fetch = originalFetch;
    }
  });

  it("customer-create passes api key to ApiClient", async () => {
    const originalFetch = global.fetch;
    global.fetch = mock.fn(async (_url, options) => {
      assert.equal(options.headers["X-API-Key"], "cli-secret");
      return {
        ok: true,
        status: 201,
        text: async () =>
          JSON.stringify({
            id: "550e8400-e29b-41d4-a716-446655440000",
            status: "pending",
            email: "jane@example.com",
          }),
      };
    });

    try {
      await customerCreate({
        name: "Jane Doe",
        email: "jane@example.com",
        phone: "9876543210",
        apiUrl: "http://localhost:8000",
        apiKey: "cli-secret",
      });
    } finally {
      global.fetch = originalFetch;
    }
  });

  it("submit-kyc validates PAN and IFSC", async () => {
    await assert.rejects(
      () =>
        submitKyc({
          customerId: "550e8400-e29b-41d4-a716-446655440000",
          pan: "BAD",
          account: "123456789012",
          ifsc: "HDFC0001234",
          apiUrl: "http://localhost:8000",
        }),
      ValidationError
    );
  });

  it("submit-kyc submits to API", async () => {
    const originalFetch = global.fetch;
    global.fetch = mock.fn(async (_url, options) => {
      const body = JSON.parse(options.body);
      assert.equal(body.pan, "ABCDE1234F");
      return {
        ok: true,
        status: 201,
        text: async () =>
          JSON.stringify({
            customer_id: body.customer_id,
            kyc_submission_id: "660e8400-e29b-41d4-a716-446655440001",
            status: "verified",
            pan_verification_status: "verified",
            bank_verification_status: "verified",
          }),
      };
    });

    try {
      const result = await submitKyc({
        customerId: "550e8400-e29b-41d4-a716-446655440000",
        pan: "ABCDE1234F",
        account: "123456789012",
        ifsc: "HDFC0001234",
        apiUrl: "http://localhost:8000",
      });
      assert.equal(result.status, "verified");
    } finally {
      global.fetch = originalFetch;
    }
  });
});
