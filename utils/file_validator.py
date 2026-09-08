import os
ALLOWED_FILES = {
    "VIDEO": {
        "extentions": {".mp4", ".mov", ".webm"},
        "mimetypes": {
            "video/mp4",
            "video/quicktime",
            "video/webm"
        },
        "max_size": 500 * 1024 *1024
    },
    "DOCUMENT": {
        "extentions": {".pdf", ".doc", ".docx", ".ppt"},
        "mimetypes": {
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-powerpoint"
        },
        "max-size": 25 * 1024 * 1024
    }
}

def validate_extension(filename, content_type):
    extension = os.path.splitext(filename)[1].lower()

    allowed_extensions = ALLOWED_FILES[content_type]["extentions"]

    if extension not in allowed_extensions:
        return False, (
            f"unsupported file extension '{extension}',",
            f"Allowed extensions {allowed_extensions}"
        )
    return True, None

def validate_mimetype(filename, content_type):
    allowed_mimetype =[content_type]["mimetypes"]

    if filename.mimetype not in allowed_mimetype:
        return False, (
            f"Usupported file type '{filename.mimetype}'"
        )
    return True, None


def validate_file(file, content_type):
    if content_type not in ALLOWED_FILES:
        return False, "Unsupported content type."
    if not file.filename:
        return False, "Filename is required."
    
    valid, error = validate_extension(file.filename, content_type)
    if not valid:
        return False, error
    
    valid, error = validate_mimetype(file, content_type)
    if not valid:
        return False, error
    