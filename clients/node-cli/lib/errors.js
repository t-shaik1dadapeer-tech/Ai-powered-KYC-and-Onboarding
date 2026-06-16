class CliError extends Error {
  constructor(message, code = "cli_error") {
    super(message);
    this.name = "CliError";
    this.code = code;
  }
}

class ValidationError extends CliError {
  constructor(message) {
    super(message, "validation_error");
    this.name = "ValidationError";
  }
}

class ApiError extends CliError {
  constructor(message, statusCode, code = "api_error") {
    super(message, code);
    this.name = "ApiError";
    this.statusCode = statusCode;
  }
}

class AnalyzerError extends CliError {
  constructor(message, exitCode = 1) {
    super(message, "analyzer_error");
    this.name = "AnalyzerError";
    this.exitCode = exitCode;
  }
}

module.exports = { CliError, ValidationError, ApiError, AnalyzerError };
