"""
Migration script: normalise every project.case_study value to the canonical
S3 key format  case_studies/<project_id>.<ext>

Any current value that already matches the target is left alone.
Everything else (old prefix, bare filenames, etc.) is rewritten using
the project's own UUID and whatever file extension can be extracted.

Run:
    python scripts/migrate_case_study_paths.py [--dry-run]

Requires the virtualenv to be active and .env to be present.
"""

import argparse
import asyncio
import logging
import re

from sqlalchemy import select, text

from app.core.connections.postgres import get_db
from app.models.projects import Projects

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

_UUID = (
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}"
    r"-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)

_TARGET_RE = re.compile(rf"^case_studies/{_UUID}\.\w{{1,5}}$")
_EXT_RE = re.compile(r"\.\w{1,5}$")


def _extract_ext(value: str) -> str:
    m = _EXT_RE.search(value)
    return m.group(0) if m else ".pdf"


def _new_key(project_id: str, ext: str) -> str:
    return f"case_studies/{project_id}{ext}"


async def migrate(dry_run: bool = False) -> None:
    async for db in get_db():
        result = await db.execute(
            select(Projects).where(Projects.case_study.isnot(None))
        )
        projects = result.scalars().all()

        log.info("Found %d projects with a case_study value", len(projects))

        updated = 0
        skipped = 0

        for project in projects:
            old_key: str = project.case_study
            pid = str(project.project_id)

            target = _new_key(pid, _extract_ext(old_key))

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
                    text("UPDATE projects SET case_study = :new WHERE project_id = :pid"),
                    {"new": target, "pid": project.project_id},
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
