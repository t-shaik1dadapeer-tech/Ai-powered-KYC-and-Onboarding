import hashlib

from app.core.exceptions import VerificationError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Mock deny-list for demonstration
INVALID_PAN_SUFFIXES = {"0000A", "XXXXX"}


def hash_sensitive(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


class PanVerificationService:
    def verify(self, pan: str) -> tuple[str, dict]:
        """Returns (status, provider_response). status: verified | rejected."""
        last_five = pan[5:]
        if any(pan.endswith(s) or last_five.startswith("0000") for s in INVALID_PAN_SUFFIXES):
            logger.warning("pan_verification_rejected", pan_masked=f"{pan[:2]}***")
            raise VerificationError("PAN verification failed with provider")

        response = {"provider": "mock", "pan_valid": True, "name_match": True}
        logger.info("pan_verification_success", pan_hash=hash_sensitive(pan)[:8])
        return "verified", response
