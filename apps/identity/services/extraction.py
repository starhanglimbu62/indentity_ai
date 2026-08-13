from datetime import date


class IdentityExtractionService:
    @staticmethod
    def extract(ocr_data: dict) -> dict:
        if not isinstance(ocr_data, dict):
            raise ValueError("OCR output must be a dictionary.")

        name = str(ocr_data.get("name", "")).strip()
        nid = str(ocr_data.get("nid", "")).strip()
        dob = ocr_data.get("dob")
        address = str(ocr_data.get("address", "")).strip()
        confidence = float(ocr_data.get("confidence", 0.0) or 0.0)

        if isinstance(dob, date):
            dob = dob.isoformat()

        return {
            "name": name,
            "nid": nid,
            "dob": dob,
            "address": address,
            "confidence": confidence,
        }
