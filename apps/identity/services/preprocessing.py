import os

from apps.identity.models import IdentityDocument


class ImagePreprocessingService:
    @staticmethod
    def preprocess(document: IdentityDocument):
        if not document.document_file or not document.document_file.name:
            return None

        file_path = document.document_file.path
        if not file_path or not os.path.exists(file_path):
            return file_path

        extension = os.path.splitext(file_path)[1].lower()
        if extension == ".pdf":
            return file_path

        try:
            from PIL import Image, ImageOps
        except ImportError:
            return file_path

        try:
            with Image.open(file_path) as image:
                image = ImageOps.exif_transpose(image)
                image = image.convert("RGB")
                image = image.resize((image.width * 2, image.height * 2))

                output_dir = os.path.join(os.path.dirname(file_path), "preprocessed")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"{document.id}.jpg")
                image.save(output_path, format="JPEG", quality=90)
                return output_path
        except Exception:
            return file_path
