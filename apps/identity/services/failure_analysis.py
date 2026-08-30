from __future__ import annotations


class IdentityFailureAnalysisService:
    """Translate a failed identity check into actionable remediation guidance."""

    @staticmethod
    def analyze(reason: str, metadata: dict | None = None) -> dict:
        metadata = metadata or {}
        normalized_reason = (reason or "Identity verification failed").strip()
        nid = str(metadata.get("nid", "")).strip()
        confidence = float(metadata.get("confidence", 0.0) or 0.0)

        invalid_nid = not nid or "invalid" in nid.lower()
        low_confidence = confidence < 0.75

        if invalid_nid and low_confidence:
            recommendation = (
                "Re-upload a high-contrast image and verify the NID value matches "
                "the document before retrying."
            )
            recoverable = False
        elif invalid_nid:
            recommendation = "Check the submitted NID and re-scan the document with a clearer photo."
            recoverable = False
        elif low_confidence:
            recommendation = "Improve image quality, lighting, and document alignment before retrying."
            recoverable = True
        else:
            recommendation = "Review the submitted document for missing or unreadable identity fields."
            recoverable = True

        return {
            "reason": normalized_reason,
            "recommendation": recommendation,
            "recoverable": recoverable,
        }
