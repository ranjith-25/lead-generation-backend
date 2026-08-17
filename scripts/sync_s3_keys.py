"""
Migration script: copy/rename S3 objects to match the canonical keys
written by the DB migration scripts.

For profile variants:
    DB key:  profile-variants/<user_id>/<pv_id>_<name>.pdf
    S3 may have the file under any of:
        - ranjith_mg_backend_profile.pdf                    (bare filename)
        - uploads/profile-variants/<uid>/<pvid>_*.pdf       (old prefix)
        - profile-variants/<uid>/<pvid>.pdf                  (old format, no name)
        - profile-variants/<uid>/<pvid>_<name>.pdf           (already correct)

For case studies:
    DB key:  case_studies/<project_id>.<ext>
    S3 may have the file under:
        - case-studies/<project_id>.<ext>    (old prefix)
        - AdilasTech_8d60a85f.pdf            (bare filename, short hash)
        - case_studies/<project_id>.<ext>    (already correct)

Run:
    python scripts/sync_s3_keys.py [--dry-run] [--delete-old]

Requires the virtualenv to be active and .env to be present.
"""

import argparse
import asyncio
import logging
import re
from collections import defaultdict
from pathlib import PurePosixPath

import aioboto3

from sqlalchemy import select

from app.core.connections.postgres import get_db
from app.core.settings import settings
from app.models.projects import Projects
from app.models.profile_variant import ProfileVariant

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

_UUID_RE = (
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}"
    r"-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)


def _ext(value: str) -> str:
    m = re.search(r"\.\w{1,5}$", value)
    return m.group(0) if m else ".pdf"


# ---------------------------------------------------------------------------
# S3 helpers
# ---------------------------------------------------------------------------

async def _list_all_objects(s3) -> list[dict]:
    """Return every object (Key, Size) in the bucket."""
    objects: list[dict] = []
    paginator = s3.get_paginator("list_objects_v2")
    async for page in paginator.paginate(Bucket=settings.AWS_S3_BUCKET):
        for obj in page.get("Contents", []):
            objects.append({"Key": obj["Key"], "Size": obj.get("Size", 0)})
    return objects


async def _copy(s3, src: str, dst: str, delete_old: bool, dry_run: bool) -> bool:
    tag = "WOULD COPY" if dry_run else "COPYING"
    log.info("%s  %s  ->  %s", tag, src, dst)
    if dry_run:
        return True
    await s3.copy_object(
        Bucket=settings.AWS_S3_BUCKET,
        CopySource={"Bucket": settings.AWS_S3_BUCKET, "Key": src},
        Key=dst,
    )
    if delete_old and src != dst:
        log.info("DELETING  %s", src)
        await s3.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=src)
    return True


# ---------------------------------------------------------------------------
# Profile-variant sync
# ---------------------------------------------------------------------------

async def _sync_profile_variants(s3, objects: list[dict], dry_run: bool, delete_old: bool) -> int:
    all_keys = {o["Key"] for o in objects}

    # Build indexes for fast lookup
    # key -> list of S3 keys
    by_user_folder: dict[str, list[str]] = defaultdict(list)   # user_id from path
    by_pv_id_in_name: dict[str, list[str]] = defaultdict(list) # pv_id in basename
    by_pv_id_anywhere: dict[str, list[str]] = defaultdict(list) # pv_id anywhere in key

    for o in objects:
        key = o["Key"]
        parts = key.split("/")

        # Extract user_id from path (profile-variants/<user_id>/...)
        if len(parts) >= 3 and parts[0] in ("profile-variants", "uploads"):
            # could be profile-variants/<uid>/... or uploads/profile-variants/<uid>/...
            for i, p in enumerate(parts):
                if p in ("profile-variants",) and i + 1 < len(parts):
                    candidate_uid = parts[i + 1]
                    if re.fullmatch(_UUID_RE, candidate_uid):
                        by_user_folder[candidate_uid].append(key)
                    break

        basename = PurePosixPath(key).stem
        # Check for pv_id as a prefix of the basename (e.g. <pv_id>.pdf or <pv_id>_name.pdf)
        for m in re.finditer(_UUID_RE, basename):
            pv_id = m.group(0)
            by_pv_id_in_name[pv_id].append(key)
            break

        # Check for pv_id anywhere in the full key
        for m in re.finditer(_UUID_RE, key):
            pv_id = m.group(0)
            by_pv_id_anywhere[pv_id].append(key)
            break

    async for db in get_db():
        result = await db.execute(select(ProfileVariant))
        variants = result.scalars().all()

    log.info("Profile variants to check: %d", len(variants))
    copied = 0

    for pv in variants:
        new_key: str = pv.upload_profile
        if new_key in all_keys:
            continue  # already at the right place

        pvid = str(pv.profile_variant_id)
        uid = str(pv.user_id)
        candidates: list[str] = []

        # Strategy 1: pv_id in basename (e.g. profile-variants/<uid>/<pvid>.pdf)
        candidates = by_pv_id_in_name.get(pvid, [])

        # Strategy 2: pv_id anywhere in key (e.g. uploads/profile-variants/<uid>/<pvid>_name.pdf)
        if not candidates:
            candidates = by_pv_id_anywhere.get(pvid, [])

        # Strategy 3: same user_id folder (narrow by extension)
        if not candidates:
            ext = _ext(new_key)
            candidates = [
                k for k in by_user_folder.get(uid, [])
                if k.endswith(ext)
            ]

        # Strategy 4: pv_id in the full key path (not just basename)
        if not candidates:
            for key in all_keys:
                if pvid in key:
                    candidates.append(key)

        if not candidates:
            log.warning(
                "No S3 object found for profile_variant %s (user %s, expected: %s)",
                pvid, uid, new_key,
            )
            continue

        # Prefer the best candidate
        src = candidates[0]
        for c in candidates:
            basename = PurePosixPath(c).stem
            # Prefer one with a human-readable name (has underscore but isn't just the UUID)
            if "_" in basename and basename != pvid:
                src = c
                break

        if await _copy(s3, src, new_key, delete_old, dry_run):
            copied += 1

    return copied


# ---------------------------------------------------------------------------
# Case-study sync
# ---------------------------------------------------------------------------

async def _sync_case_studies(s3, objects: list[dict], dry_run: bool, delete_old: bool) -> int:
    all_keys = {o["Key"] for o in objects}

    # Build index: project_id -> list of S3 keys
    by_project_id: dict[str, list[str]] = defaultdict(list)
    by_old_prefix: dict[str, list[str]] = defaultdict(list)

    for o in objects:
        key = o["Key"]
        basename = PurePosixPath(key).name

        # Match project UUID anywhere in the key
        for m in re.finditer(_UUID_RE, key):
            pid = m.group(0)
            by_project_id[pid].append(key)
            break

        # Match old prefix case-studies/<uuid>.<ext>
        m = re.match(rf"^case-studies/({_UUID_RE})\.\w{{1,4}}$", key)
        if m:
            by_old_prefix[m.group(1)].append(key)

    async for db in get_db():
        result = await db.execute(
            select(Projects).where(Projects.case_study.isnot(None))
        )
        projects = result.scalars().all()

    log.info("Projects with case_study to check: %d", len(projects))
    copied = 0

    for proj in projects:
        new_key: str = proj.case_study
        if new_key in all_keys:
            continue

        pid = str(proj.project_id)
        ext = _ext(new_key)
        candidates: list[str] = []

        # Strategy 1: old prefix case-studies/<pid>.<ext>
        candidates = by_old_prefix.get(pid, [])

        # Strategy 2: project_id anywhere in key with matching extension
        if not candidates:
            candidates = [
                k for k in by_project_id.get(pid, [])
                if k.endswith(ext)
            ]

        # Strategy 3: project_id anywhere in any key
        if not candidates:
            candidates = by_project_id.get(pid, [])

        if not candidates:
            log.warning(
                "No S3 object found for project %s (expected: %s)",
                pid, new_key,
            )
            continue

        src = candidates[0]
        if await _copy(s3, src, new_key, delete_old, dry_run):
            copied += 1

    return copied


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main(dry_run: bool, delete_old: bool) -> None:
    session = aioboto3.Session()
    async with session.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    ) as s3:
        log.info("Listing all objects in s3://%s ...", settings.AWS_S3_BUCKET)
        objects = await _list_all_objects(s3)
        log.info("Total objects in bucket: %d", len(objects))

        pv_copied = await _sync_profile_variants(s3, objects, dry_run, delete_old)
        cs_copied = await _sync_case_studies(s3, objects, dry_run, delete_old)

    log.info("Done.  profile_variants_copied=%d  case_studies_copied=%d", pv_copied, cs_copied)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Preview without touching S3.")
    parser.add_argument("--delete-old", action="store_true", help="Delete the old object after a successful copy.")
    args = parser.parse_args()
    asyncio.run(main(dry_run=args.dry_run, delete_old=args.delete_old))
