const { describe, it, mock } = require("node:test");
const assert = require("node:assert/strict");
const { ApiClient } = require("../lib/api-client");
const { ApiError } = require("../lib/errors");

describe("ApiClient", () => {
  it("creates customer via POST /customers", async () => {
    const fetchMock = mock.fn(async (url, options) => {
      assert.equal(url, "http://localhost:8000/customers");
      assert.equal(options.method, "POST");
      const body = JSON.parse(options.body);
      assert.equal(body.full_name, "Jane Doe");
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

    const client = new ApiClient("http://localhost:8000", fetchMock);
    const result = await client.createCustomer({
      fullName: "Jane Doe",
      email: "jane@example.com",
      phone: "9876543210",
    });
    assert.equal(result.status, "pending");
    assert.equal(fetchMock.mock.calls.length, 1);
  });

  it("throws ApiError on HTTP error response", async () => {
    const fetchMock = mock.fn(async () => ({
      ok: false,
      status: 409,
      text: async () =>
        JSON.stringify({ error: { code: "conflict", message: "Email already exists" } }),
    }));

    const client = new ApiClient("http://localhost:8000", fetchMock);
    await assert.rejects(
      () =>
        client.createCustomer({
          fullName: "Jane",
          email: "jane@example.com",
          phone: "9876543210",
        }),
      (err) => {
        assert.ok(err instanceof ApiError);
        assert.equal(err.statusCode, 409);
        assert.match(err.message, /already exists/);
        return true;
      }
    );
  });

  it("throws ApiError on network failure", async () => {
    const fetchMock = mock.fn(async () => {
      throw new Error("connection refused");
    });
    const client = new ApiClient("http://localhost:8000", fetchMock);
    await assert.rejects(
      () => client.getHealth(),
      (err) => err.code === "network_error"
    );
  });

  it("sends X-API-Key header when apiKey is configured", async () => {
    const fetchMock = mock.fn(async (_url, options) => {
      assert.equal(options.headers["X-API-Key"], "secret-key");
      return {
        ok: true,
        status: 200,
        text: async () => JSON.stringify({ status: "healthy" }),
      };
    });

    const client = new ApiClient("http://localhost:8000", fetchMock, "secret-key");
    await client.getHealth();
    assert.equal(fetchMock.mock.calls.length, 1);
  });
});
