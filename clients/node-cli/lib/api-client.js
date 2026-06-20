const { ApiError } = require("./errors");

class ApiClient {
  constructor(baseUrl, fetchImpl = global.fetch, apiKey = undefined) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.fetch = fetchImpl;
    this.apiKey = apiKey || undefined;
  }

  async createCustomer({ fullName, email, phone }) {
    return this._request("POST", "/customers", {
      full_name: fullName,
      email,
      phone,
    });
  }

  async submitKyc({ customerId, pan, accountNumber, ifsc }) {
    return this._request("POST", "/kyc", {
      customer_id: customerId,
      pan,
      account_number: accountNumber,
      ifsc,
    });
  }

  async getHealth() {
    return this._request("GET", "/health");
  }

  async _request(method, path, body) {
    const url = `${this.baseUrl}${path}`;
    const options = {
      method,
      headers: { "Content-Type": "application/json", Accept: "application/json" },
    };
    if (this.apiKey) {
      options.headers["X-API-Key"] = this.apiKey;
    }
    if (body !== undefined) {
      options.body = JSON.stringify(body);
    }

    let response;
    try {
      response = await this.fetch(url, options);
    } catch (err) {
      throw new ApiError(`Failed to reach API at ${url}: ${err.message}`, 0, "network_error");
    }

    const text = await response.text();
    let data = null;
    if (text) {
      try {
        data = JSON.parse(text);
      } catch {
        data = { raw: text };
      }
    }

    if (!response.ok) {
      const message =
        data?.error?.message ||
        data?.detail?.[0]?.msg ||
        data?.detail ||
        `HTTP ${response.status}`;
      const code = data?.error?.code || "api_error";
      throw new ApiError(String(message), response.status, code);
    }

    return data;
  }
}

module.exports = { ApiClient };
