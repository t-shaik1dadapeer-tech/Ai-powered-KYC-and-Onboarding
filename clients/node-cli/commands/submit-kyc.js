const { ApiClient } = require("../lib/api-client");
const {
  validateAccountNumber,
  validateCustomerId,
  validateIfsc,
  validatePan,
} = require("../lib/validators");

async function submitKyc(options) {
  const customerId = validateCustomerId(options.customerId);
  const pan = validatePan(options.pan);
  const accountNumber = validateAccountNumber(options.account);
  const ifsc = validateIfsc(options.ifsc);

  const client = new ApiClient(options.apiUrl);
  const result = await client.submitKyc({
    customerId,
    pan,
    accountNumber,
    ifsc,
  });

  return {
    customerId: result.customer_id,
    kycSubmissionId: result.kyc_submission_id,
    status: result.status,
    panStatus: result.pan_verification_status,
    bankStatus: result.bank_verification_status,
    raw: result,
  };
}

module.exports = { submitKyc };
