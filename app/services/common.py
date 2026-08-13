from app.models.user_personal_info import UserPersonalInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def change_dob_format(db: AsyncSession):
    users = await db.execute(select(UserPersonalInfo).where(UserPersonalInfo.date_of_birth.ilike("____-__-__")))
    users = users.scalars().all()
    
    for user in users:
        user.date_of_birth = "/".join((user.date_of_birth.split("-"))[::-1])
    await db.commit()
    return users