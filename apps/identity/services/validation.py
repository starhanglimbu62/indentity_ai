import os
import re
from datetime import datetime

MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "application/pdf"}
NID_PATTERN = re.compile(r"^\d{10,20}$")


class DocumentValidationService:
    @staticmethod
    def validate_file(file_obj) -> None:
        if file_obj is None:
            raise ValueError("Document file is required.")

        file_name = getattr(file_obj, "name", "") or ""
        if not file_name:
            raise ValueError("Document file is required.")

        extension = os.path.splitext(file_name)[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError("Unsupported file type. Use JPG, JPEG, PNG, or PDF.")

        content_type = getattr(file_obj, "content_type", "") or ""
        if content_type and content_type not in ALLOWED_MIME_TYPES:
            raise ValueError("Unsupported MIME type for the uploaded document.")

        file_size = getattr(file_obj, "size", 0) or 0
        if file_size <= 0:
            raise ValueError("The uploaded document is empty.")
        if file_size > MAX_FILE_SIZE:
            raise ValueError("The uploaded document exceeds the 10MB file limit.")


class IdentityValidationService:
    @staticmethod
    def validate(extracted_data: dict) -> dict:
        if not isinstance(extracted_data, dict):
            raise ValueError("Identity data must be a dictionary.")

        name = str(extracted_data.get("name", "")).strip()
        nid = str(extracted_data.get("nid", "")).strip()
        dob = extracted_data.get("dob")
        confidence = float(extracted_data.get("confidence", 0) or 0)

        if not name:
            raise ValueError("Missing required field: name.")
        if not nid:
            raise ValueError("Missing required field: NID.")
        if not dob:
            raise ValueError("Missing required field: date of birth.")
        if confidence < 0.75:
            raise ValueError("OCR confidence is below the required threshold.")

        if not NID_PATTERN.match(nid):
            raise ValueError("Invalid NID format.")

        try:
            parsed_dob = datetime.strptime(str(dob), "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("Invalid date of birth format.") from exc

        return {
            "name": name,
            "nid": nid,
            "dob": parsed_dob,
            "address": str(extracted_data.get("address", "")).strip(),
            "confidence": confidence,
        }
