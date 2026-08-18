import uuid
from fastapi import UploadFile

from app.core.settings import settings
from app.exceptions.project import (
    CaseStudyEmptyException,
    CaseStudyTooLargeException,
    CaseStudyUnsupportedTypeException,
)

ALLOWED_CASE_STUDY_EXTENSIONS = {".pdf", ".doc", ".docx"}


def has_upload(file: UploadFile | None) -> bool:
    """
    Check if the UploadFile exists and contains a filename.
    """
    # An omitted multipart field arrives as None, but some clients send an empty part instead
    return file is not None and bool(file.filename)


class SizeLimitingReader:
    """
    A wrapper around a file object that limits the number of bytes read
    to prevent large files from being uploaded to S3.
    """
    def __init__(self, file_obj, max_bytes: int, limit_mb: float):
        self.file_obj = file_obj
        self.max_bytes = max_bytes
        self.limit_mb = limit_mb
        self.bytes_read = 0

    def read(self, size=-1):
        data = self.file_obj.read(size)
        self.bytes_read += len(data)
        if self.bytes_read > self.max_bytes:
            # If the streamed content exceeds the maximum bytes limit, raise an error
            raise CaseStudyTooLargeException(self.limit_mb)
        return data