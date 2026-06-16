from prometheus_client import Counter, Gauge, Histogram

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

CUSTOMERS_CREATED_TOTAL = Counter(
    "customers_created_total",
    "Total customers created",
    ["status"],
)

KYC_SUBMISSIONS_TOTAL = Counter(
    "kyc_submissions_total",
    "Total KYC submissions",
    ["status"],
)

PAN_VERIFICATIONS_TOTAL = Counter(
    "pan_verifications_total",
    "Total PAN verification attempts",
    ["status"],
)

BANK_VERIFICATIONS_TOTAL = Counter(
    "bank_verifications_total",
    "Total bank verification attempts",
    ["status"],
)

RISK_ASSESSMENTS_TOTAL = Counter(
    "risk_assessments_total",
    "Total risk score calculations",
    ["band"],
)

RISK_SCORE_OBSERVATIONS = Histogram(
    "risk_score_histogram",
    "Observed risk scores",
    ["band"],
    buckets=(10, 20, 30, 40, 50, 60, 70, 80, 90, 100),
)

ACTIVE_KYC_SUBMISSIONS = Gauge(
    "kyc_submissions_active",
    "KYC submissions currently in verified status (cumulative successful count proxy)",
)
