from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.sales_enablement import SalesEnablement

async def add_sales_enablement_db(db: AsyncSession, sales_enablement: SalesEnablement) -> SalesEnablement:
    db.add(sales_enablement)
    await db.commit()
    await db.refresh(sales_enablement)
    return sales_enablement

async def get_sales_enablement_by_id_db(db: AsyncSession, se_id) -> SalesEnablement | None:
    result = await db.execute(select(SalesEnablement).where(SalesEnablement.id == se_id))
    return result.scalars().first()

async def get_sales_enablement_by_opp_db(db: AsyncSession, opportunity_id) -> SalesEnablement | None:
    result = await db.execute(select(SalesEnablement).where(SalesEnablement.opportunityID == opportunity_id))
    return result.scalars().first()

async def update_sales_enablement_db(db: AsyncSession, sales_enablement: SalesEnablement, update_data: dict) -> SalesEnablement:
    for key, value in update_data.items():
        setattr(sales_enablement, key, value)
    db.add(sales_enablement)
    await db.commit()
    await db.refresh(sales_enablement)
    return sales_enablement

async def delete_sales_enablement_db(db: AsyncSession, sales_enablement: SalesEnablement) -> None:
    await db.delete(sales_enablement)
    await db.commit()
