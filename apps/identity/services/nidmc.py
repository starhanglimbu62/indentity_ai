import re


class NIDMCService:
    @staticmethod
    def verify_identity(nid: str) -> bool:
        if not nid:
            return False

        normalized_nid = str(nid).strip()
        if re.fullmatch(r"\d{10,20}", normalized_nid) is None:
            return False

        if normalized_nid in {"0000000000", "INVALIDNID"}:
            return False

        return True
