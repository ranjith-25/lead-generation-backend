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

# every upload lands under <project root>/uploads/, so a stored path means the same thing
# no matter which directory the process happens to be started from
PROJECT_ROOT = Path(__file__).resolve().parents[2]
UPLOAD_ROOT = PROJECT_ROOT / "uploads"

# an absolute CASE_STUDY_DIR is honoured as-is; a relative one hangs off the project root
CASE_STUDY_DIR = (PROJECT_ROOT / settings.CASE_STUDY_DIR).resolve()

_CHUNK_SIZE = 1024 * 1024
_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")


def has_upload(file: UploadFile | None) -> bool:
    # an omitted multipart field arrives as None, but some clients send an empty part instead
    return file is not None and bool(file.filename)


def _stored_name(original_name: str) -> str:
    source = Path(original_name)
    stem = _UNSAFE_CHARS.sub("-", source.stem).strip("-.")[:60] or "case-study"
    return f"{stem}_{uuid.uuid4().hex[:8]}{source.suffix.lower()}"


def _to_stored_path(destination: Path) -> str:
    """The value persisted on the row — relative to the project root whenever possible."""

    try:
        return destination.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        # CASE_STUDY_DIR was pointed somewhere outside the project; nothing to be relative to
        return destination.as_posix()


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

    return _to_stored_path(destination)


def resolve_case_study(stored_path: str | None) -> Path | None:
    """Absolute path of a stored document, or None if it is missing or outside the store."""

    if not stored_path:
        return None

    # stored values are project-root relative; an absolute one is left alone by `/`
    candidate = (PROJECT_ROOT / stored_path).resolve()

    # a stored path is only ever read back out of our own directory — anything else is tampering
    if CASE_STUDY_DIR not in candidate.parents:
        return None

    return candidate if candidate.is_file() else None


def delete_case_study(stored_path: str | None) -> None:
    resolved = resolve_case_study(stored_path)
    if resolved:
        resolved.unlink(missing_ok=True)


async def save_profile_variant(file: UploadFile, user_id: uuid.UUID, profile_variant_id: uuid.UUID) -> str:
    """Write an uploaded profile variant PDF to disk and return the path stored in DB."""

    filename = file.filename or ""
    extension = Path(filename).suffix.lower()
    if extension != ".pdf":
        from fastapi.exceptions import RequestValidationError
        raise RequestValidationError(
            [
                {
                    "type": "value_error",
                    "loc": ("body", "upload_profile"),
                    "msg": "Only PDF files are allowed",
                    "input": filename,
                }
            ]
        )

    # <project root>/uploads/profile-variants/<user_id>/<profile_variant_id>_<original-filename>.pdf
    upload_dir = UPLOAD_ROOT / "profile-variants" / str(user_id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    destination = upload_dir / f"{profile_variant_id}_{filename}"

    await file.seek(0)
    try:
        with destination.open("wb") as target:
            while chunk := await file.read(_CHUNK_SIZE):
                target.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()

    return _to_stored_path(destination)