# Test Inventory

Total: **26**

| name | file | line |
| --- | --- | --- |
| test_bug001_isolation_first_run | tests/test_bug001_regression.py | 17 |
| test_bug001_isolation_second_run | tests/test_bug001_regression.py | 22 |
| test_create_customer | tests/test_customers.py | 1 |
| test_create_customer_duplicate_email | tests/test_customers.py | 17 |
| test_create_customer_normalizes_email_case | tests/test_customers.py | 29 |
| test_create_customer_duplicate_email_different_case | tests/test_customers.py | 42 |
| test_create_customer_invalid_email | tests/test_customers.py | 54 |
| test_get_customer | tests/test_customers.py | 62 |
| test_get_customer_not_found | tests/test_customers.py | 69 |
| test_health | tests/test_health.py | 1 |
| test_metrics | tests/test_health.py | 9 |
| test_full_kyc_onboarding_flow | tests/test_integration.py | 3 |
| test_health_and_metrics_available | tests/test_integration.py | 46 |
| test_submit_kyc_success | tests/test_kyc.py | 1 |
| test_submit_kyc_invalid_pan | tests/test_kyc.py | 18 |
| test_submit_kyc_rejected_pan | tests/test_kyc.py | 31 |
| test_get_kyc_status | tests/test_kyc.py | 44 |
| test_get_kyc_status_not_found | tests/test_kyc.py | 59 |
| test_kyc_flow_exposes_domain_metrics | tests/test_metrics.py | 16 |
| test_risk_score_without_kyc | tests/test_risk.py | 1 |
| test_risk_score_after_kyc | tests/test_risk.py | 10 |
| test_risk_score_customer_not_found | tests/test_risk.py | 27 |
| test_pan_verify_success | tests/test_verification.py | 1 |
| test_pan_verify_invalid_format | tests/test_verification.py | 10 |
| test_bank_verify_success | tests/test_verification.py | 18 |
| test_bank_verify_invalid_account | tests/test_verification.py | 31 |
