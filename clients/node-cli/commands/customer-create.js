const { ApiClient } = require("../lib/api-client");
const {
  validateEmail,
  validateFullName,
  validatePhone,
} = require("../lib/validators");

async function customerCreate(options) {
  const fullName = validateFullName(options.name);
  const email = validateEmail(options.email);
  const phone = validatePhone(options.phone);

  const client = new ApiClient(options.apiUrl, global.fetch, options.apiKey);
  const result = await client.createCustomer({ fullName, email, phone });

  return {
    customerId: result.id,
    status: result.status,
    email: result.email,
    raw: result,
  };
}

module.exports = { customerCreate };
