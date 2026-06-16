# KYC CLI

Node.js client for the onboarding API and repository intelligence engine.

## Requirements

- Node.js 18+ (native `fetch`)
- Python 3.9+ (for `generate-report` only)

## Install

```bash
cd clients/node-cli
npm install
chmod +x bin/kyc-cli.js
```

## Commands

### customer-create

```bash
node bin/kyc-cli.js customer-create \
  --name "Jane Doe" \
  --email "jane@example.com" \
  --phone "9876543210" \
  --api-url http://localhost:8000
```

### submit-kyc

```bash
node bin/kyc-cli.js submit-kyc \
  --customer-id "<UUID>" \
  --pan "ABCDE1234F" \
  --account "123456789012" \
  --ifsc "HDFC0001234"
```

### generate-report

```bash
node bin/kyc-cli.js generate-report \
  --path ../../services/onboarding-api \
  --output ../../reports/onboarding-api
```

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `API_BASE_URL` | `http://localhost:8000` | Onboarding API base URL |

## Test

```bash
npm test
```

Uses Node.js built-in test runner (no Jest/Vitest dependency).

## Architecture

- `lib/validators.js` — client-side validation (PAN, IFSC, email, UUID)
- `lib/api-client.js` — HTTP client for FastAPI
- `lib/analyzer-client.js` — spawns Python intelligence engine
- `commands/` — command handlers (no business logic duplication)
