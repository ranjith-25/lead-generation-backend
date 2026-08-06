import re
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.settings import settings
from app.exceptions.project import (
    CaseStudyEmptyException,
    CaseStudyTooLargeException,
    CaseStudyUnsupportedTypeException,
)

ALLOWED_CASE_STUDY_EXTENSIONS = {".pdf", ".doc", ".docx"}

CASE_STUDY_DIR = Path(settings.CASE_STUDY_DIR)

_CHUNK_SIZE = 1024 * 1024
_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")


def has_upload(file: UploadFile | None) -> bool:
    # an omitted multipart field arrives as None, but some clients send an empty part instead
    return file is not None and bool(file.filename)


def _stored_name(original_name: str) -> str:
    source = Path(original_name)
    stem = _UNSAFE_CHARS.sub("-", source.stem).strip("-.")[:60] or "case-study"
    return f"{stem}_{uuid.uuid4().hex[:8]}{source.suffix.lower()}"


async def save_case_study(file: UploadFile) -> str:
    """Write an uploaded case study to disk and return the path stored on the project row."""

    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_CASE_STUDY_EXTENSIONS:
        raise CaseStudyUnsupportedTypeException(sorted(ALLOWED_CASE_STUDY_EXTENSIONS))

    CASE_STUDY_DIR.mkdir(parents=True, exist_ok=True)
    destination = CASE_STUDY_DIR / _stored_name(file.filename)

    max_bytes = settings.MAX_CASE_STUDY_SIZE_MB * 1024 * 1024
    written = 0

    await file.seek(0)
    try:
        with destination.open("wb") as target:
            while chunk := await file.read(_CHUNK_SIZE):
                written += len(chunk)
                # the cap has to be enforced while streaming — trusting Content-Length would
                # let a lying client fill the disk before we ever check it
                if written > max_bytes:
                    raise CaseStudyTooLargeException(settings.MAX_CASE_STUDY_SIZE_MB)
                target.write(chunk)

        if written == 0:
            raise CaseStudyEmptyException()
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()

    return destination.as_posix()


def resolve_case_study(stored_path: str | None) -> Path | None:
    """Absolute path of a stored document, or None if it is missing or outside the store."""

    if not stored_path:
        return None

    base = CASE_STUDY_DIR.resolve()
    candidate = Path(stored_path).resolve()

    # a stored path is only ever read back out of our own directory — anything else is tampering
    if base not in candidate.parents:
        return None

    return candidate if candidate.is_file() else None


def delete_case_study(stored_path: str | None) -> None:
    resolved = resolve_case_study(stored_path)
    if resolved:
        resolved.unlink(missing_ok=True)
