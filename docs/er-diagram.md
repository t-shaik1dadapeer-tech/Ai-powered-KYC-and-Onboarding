# Entity-Relationship Diagram

**Source of truth:** SQLAlchemy ORM models in `services/onboarding-api/app/models/`  
**No Alembic migrations** — schema from `Base.metadata.create_all()` in `app/main.py`

---

## Entity List

| Entity | Table | Primary Key | Source File |
|--------|-------|-------------|-------------|
| Customer | `customers` | `id` (UUID) | `app/models/customer.py:14` |
| KycSubmission | `kyc_submissions` | `id` (UUID) | `app/models/kyc.py:16` |
| PanRecord | `pan_records` | `id` (UUID) | `app/models/kyc.py:37` |
| BankRecord | `bank_records` | `id` (UUID) | `app/models/kyc.py:51` |
| RiskAssessment | `risk_assessments` | `id` (UUID) | `app/models/risk.py:15` |

---

## Relationships (with FK citations)

| From | To | Cardinality | FK Column | Source |
|------|-----|-------------|-----------|--------|
| Customer | KycSubmission | 1:N | `kyc_submissions.customer_id` → `customers.id` | `kyc.py:17-18` |
| Customer | RiskAssessment | 1:N | `risk_assessments.customer_id` → `customers.id` | `risk.py:16-17` |
| KycSubmission | PanRecord | 1:1 | `pan_records.kyc_submission_id` → `kyc_submissions.id` (unique) | `kyc.py:38-39` |
| KycSubmission | BankRecord | 1:1 | `bank_records.kyc_submission_id` → `kyc_submissions.id` (unique) | `kyc.py:52-53` |

---

## Key Attributes

### Customer
- `email` — unique, indexed (`customer.py:16`)
- `status` — default `pending` (`customer.py:18`)

### KycSubmission
- `status` — pending | verified | rejected
- `submitted_at`, `verified_at` — timestamps

### PanRecord / BankRecord
- `pan_hash`, `account_hash` — sensitive data hashed at persistence
- `provider_response` — JSON (mock verifier output)

### RiskAssessment
- `score` — 0–100 integer
- `band` — low | medium | high
- `factors` — JSON breakdown

---

## Mermaid ER Diagram

```mermaid
erDiagram
    CUSTOMERS ||--o{ KYC_SUBMISSIONS : has
    CUSTOMERS ||--o{ RISK_ASSESSMENTS : has
    KYC_SUBMISSIONS ||--o| PAN_RECORDS : has
    KYC_SUBMISSIONS ||--o| BANK_RECORDS : has

    CUSTOMERS {
        uuid id PK
        string full_name
        string email UK
        string phone
        string status
        datetime created_at
        datetime updated_at
    }

    KYC_SUBMISSIONS {
        uuid id PK
        uuid customer_id FK
        string status
        string rejection_reason
        datetime submitted_at
        datetime verified_at
    }

    PAN_RECORDS {
        uuid id PK
        uuid kyc_submission_id FK UK
        string pan_hash
        string verification_status
        json provider_response
    }

    BANK_RECORDS {
        uuid id PK
        uuid kyc_submission_id FK UK
        string account_hash
        string ifsc
        string verification_status
        json provider_response
    }

    RISK_ASSESSMENTS {
        uuid id PK
        uuid customer_id FK
        int score
        string band
        json factors
        datetime calculated_at
    }
```

**Generated artifact:** `evidence/api-maps/onboarding-api/er-diagram.mmd`  
**Analyzer source:** `engines/intelligence/src/intelligence/generators/er_diagram.py`

---

## Verification

```bash
grep -n ForeignKey services/onboarding-api/app/models/*.py
PYTHONPATH=services/onboarding-api engines/intelligence/.venv/bin/python -m intelligence.cli \
  services/onboarding-api -o /tmp/er-check && cat /tmp/er-check/er-diagram.mmd
```
