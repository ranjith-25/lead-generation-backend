"""
Migration script: normalise every profile_variants.upload_profile value to the
canonical S3 key format:

    profile-variants/<user_id>/<profile_variant_id>_<file_name>.pdf

Any current value that already matches the target is left alone.
Everything else (bare filenames, uploads/ prefix, old paths, etc.) is
rewritten using the row's own user_id, profile_variant_id, and whatever
human-readable filename can be extracted.

Run:
    python scripts/migrate_profile_variant_paths.py [--dry-run]

Requires the virtualenv to be active and .env to be present.
"""

import argparse
import asyncio
import logging
import re
from pathlib import PurePosixPath

from sqlalchemy import select, text

from app.core.connections.postgres import get_db
from app.models.profile_variant import ProfileVariant

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

_UUID = (
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}"
    r"-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)

# Already correct:  profile-variants/<user_id>/<pv_id>_<name>.pdf
_TARGET_RE = re.compile(
    rf"^profile-variants/{_UUID}/{_UUID}_\w.+\.\w{{1,4}}$"
)

# Old path that contains a UUID-named file with a trailing human name:
#   <prefix>/<user_id>/<pv_id>_<name>.<ext>
_WITH_NAME_RE = re.compile(
    rf"(?:.+/)?({_UUID})/({_UUID})_(.+)\.\w{{1,4}}$"
)

# Old path with just a UUID-named file (no human name):
#   <prefix>/<user_id>/<pv_id>.<ext>
_UUID_ONLY_RE = re.compile(
    rf"(?:.+/)?({_UUID})/({_UUID})\.\w{{1,4}}$"
)

# Bare filename with no path at all:  some_name.pdf
_BARE_RE = re.compile(r"^([^/]+\.\w{1,4})$")

_EXT_RE = re.compile(r"\.\w{1,5}$")


def _extract_ext(value: str) -> str:
    m = _EXT_RE.search(value)
    return m.group(0) if m else ".pdf"


def _extract_file_name(old_key: str) -> str:
    """Return a human-readable stem to embed in the new key.

    Examples:
        ranjith_mg_backend_profile.pdf                               -> ranjith_mg_backend_profile
        uploads/profile-variants/.../076f81ec-..._SHANMU..._resume.pdf -> SHANMU..._resume
        profile-variants/.../fb011448-....pdf                        -> fb011448-....
    """
    # Try the "pv_id_<name>" pattern first
    m = _WITH_NAME_RE.search(old_key)
    if m:
        return m.group(3)  # the human-readable part after the second UUID

    # UUID-only file (no human name) — keep the UUID as the name
    m = _UUID_ONLY_RE.search(old_key)
    if m:
        return m.group(2)  # the profile-variant UUID itself

    # Bare filename — use the whole stem
    stem = PurePosixPath(old_key).stem
    return stem


def _new_key(user_id: str, profile_variant_id: str, file_name: str, ext: str) -> str:
    return f"profile-variants/{user_id}/{profile_variant_id}_{file_name}{ext}"


async def migrate(dry_run: bool = False) -> None:
    async for db in get_db():
        result = await db.execute(select(ProfileVariant))
        variants = result.scalars().all()

        log.info("Found %d profile variants total", len(variants))

        updated = 0
        skipped = 0

        for pv in variants:
            old_key: str = pv.upload_profile
            uid = str(pv.user_id)
            pvid = str(pv.profile_variant_id)
            ext = _extract_ext(old_key)

            file_name = _extract_file_name(old_key)
            target = _new_key(uid, pvid, file_name, ext)

            if old_key == target:
                skipped += 1
                continue

            log.info(
                "%s  %s  ->  %s",
                "WOULD UPDATE" if dry_run else "UPDATING",
                old_key,
                target,
            )

            if not dry_run:
                await db.execute(
                    text(
                        "UPDATE profile_variants "
                        "SET upload_profile = :new "
                        "WHERE profile_variant_id = :pvid"
                    ),
                    {"new": target, "pvid": pv.profile_variant_id},
                )

            updated += 1

        if not dry_run:
            await db.commit()

        log.info("Done.  updated=%d  skipped=%d", updated, skipped)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without touching the database.",
    )
    args = parser.parse_args()
    asyncio.run(migrate(dry_run=args.dry_run))
