const { ValidationError } = require("./errors");

const PAN_PATTERN = /^[A-Z]{5}[0-9]{4}[A-Z]$/;
const IFSC_PATTERN = /^[A-Z]{4}0[A-Z0-9]{6}$/;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_PATTERN = /^\+?[0-9]{10,20}$/;
const UUID_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function normalizePan(pan) {
  return pan.toUpperCase().trim();
}

function validatePan(pan) {
  const normalized = normalizePan(pan);
  if (!PAN_PATTERN.test(normalized)) {
    throw new ValidationError("Invalid PAN format. Expected ABCDE1234F");
  }
  return normalized;
}

function validateIfsc(ifsc) {
  const normalized = ifsc.toUpperCase().trim();
  if (!IFSC_PATTERN.test(normalized)) {
    throw new ValidationError("Invalid IFSC format");
  }
  return normalized;
}

function validateAccountNumber(accountNumber) {
  const cleaned = accountNumber.replace(/\s/g, "");
  if (!/^[0-9]{9,18}$/.test(cleaned)) {
    throw new ValidationError("Account number must be 9-18 digits");
  }
  return cleaned;
}

function validateEmail(email) {
  const trimmed = email.trim();
  if (!EMAIL_PATTERN.test(trimmed)) {
    throw new ValidationError("Invalid email address");
  }
  return trimmed;
}

function validatePhone(phone) {
  const trimmed = phone.trim();
  if (!PHONE_PATTERN.test(trimmed)) {
    throw new ValidationError("Invalid phone number (10-20 digits, optional + prefix)");
  }
  return trimmed;
}

function validateFullName(name) {
  const trimmed = name.trim();
  if (trimmed.length < 2 || trimmed.length > 255) {
    throw new ValidationError("Full name must be 2-255 characters");
  }
  return trimmed;
}

function validateCustomerId(customerId) {
  const trimmed = customerId.trim();
  if (!UUID_PATTERN.test(trimmed)) {
    throw new ValidationError("Customer ID must be a valid UUID");
  }
  return trimmed;
}

function validateRepoPath(repoPath) {
  const fs = require("fs");
  const path = require("path");
  const resolved = path.resolve(repoPath);
  if (!fs.existsSync(resolved) || !fs.statSync(resolved).isDirectory()) {
    throw new ValidationError(`Repository path does not exist: ${resolved}`);
  }
  return resolved;
}

module.exports = {
  PAN_PATTERN,
  IFSC_PATTERN,
  validatePan,
  validateIfsc,
  validateAccountNumber,
  validateEmail,
  validatePhone,
  validateFullName,
  validateCustomerId,
  validateRepoPath,
};
