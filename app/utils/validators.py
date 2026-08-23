"""
File upload validation — enforced consistently for every upload type
(photo, resume, certificate) in the app.
"""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def validate_file_upload(file_storage, subfolder: str, allowed_extensions: set):
    """
    Validates and saves an uploaded file. Returns the relative static path
    to store in the DB (e.g. 'uploads/photos/xxxx.jpg'), or None if the
    upload failed validation.
    """
    if not file_storage or file_storage.filename == "":
        return None

    original_name = secure_filename(file_storage.filename)
    if "." not in original_name:
        return None

    extension = original_name.rsplit(".", 1)[1].lower()
    if extension not in allowed_extensions:
        return None

    safe_filename = f"{uuid.uuid4().hex}.{extension}"
    target_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder)
    os.makedirs(target_dir, exist_ok=True)

    file_storage.save(os.path.join(target_dir, safe_filename))

    return f"uploads/{subfolder}/{safe_filename}"
