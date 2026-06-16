from app.core.exceptions import VerificationError
from app.core.logging import get_logger
from app.services.pan_verification_service import hash_sensitive

logger = get_logger(__name__)

INVALID_ACCOUNT_PREFIXES = ("000000", "999999")


class BankVerificationService:
    def verify(self, account_number: str, ifsc: str) -> tuple[str, dict]:
        if account_number.startswith(INVALID_ACCOUNT_PREFIXES):
            logger.warning("bank_verification_rejected", ifsc=ifsc)
            raise VerificationError("Bank account verification failed with provider")

        response = {
            "provider": "mock",
            "account_valid": True,
            "ifsc": ifsc,
            "account_hash": hash_sensitive(account_number)[:8],
        }
        logger.info("bank_verification_success", ifsc=ifsc)
        return "verified", response
