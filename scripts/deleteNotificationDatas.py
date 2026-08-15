from app.models.notifications import Notifications
from sqlalchemy import delete
from app.core.connections.postgres import get_db
import asyncio


async def delete_notifications(db):
    await db.execute(delete(Notifications))
    await db.commit()


async def main():
    async for db in get_db():
        await delete_notifications(db)


if __name__ == "__main__":
    asyncio.run(main())