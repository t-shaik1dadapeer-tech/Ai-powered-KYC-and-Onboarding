const { describe, it } = require("node:test");
const assert = require("node:assert/strict");
const {
  validatePan,
  validateIfsc,
  validateAccountNumber,
  validateEmail,
  validatePhone,
  validateFullName,
  validateCustomerId,
} = require("../lib/validators");
const { ValidationError } = require("../lib/errors");

describe("validators", () => {
  it("validates PAN format", () => {
    assert.equal(validatePan("abcde1234f"), "ABCDE1234F");
  });

  it("rejects invalid PAN", () => {
    assert.throws(() => validatePan("INVALID"), ValidationError);
  });

  it("validates IFSC format", () => {
    assert.equal(validateIfsc("hdfc0001234"), "HDFC0001234");
  });

  it("rejects invalid IFSC", () => {
    assert.throws(() => validateIfsc("BADIFSC"), ValidationError);
  });

  it("validates account number", () => {
    assert.equal(validateAccountNumber("123456789012"), "123456789012");
  });

  it("rejects non-numeric account", () => {
    assert.throws(() => validateAccountNumber("abc"), ValidationError);
  });

  it("validates email and phone", () => {
    assert.equal(validateEmail("user@example.com"), "user@example.com");
    assert.equal(validatePhone("+919876543210"), "+919876543210");
  });

  it("validates full name length", () => {
    assert.equal(validateFullName("Jane Doe"), "Jane Doe");
    assert.throws(() => validateFullName("J"), ValidationError);
  });

  it("validates customer UUID", () => {
    const id = "550e8400-e29b-41d4-a716-446655440000";
    assert.equal(validateCustomerId(id), id);
    assert.throws(() => validateCustomerId("not-a-uuid"), ValidationError);
  });
});
