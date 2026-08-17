import logging
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.firebase_token import FirebaseTokens


async def get_all_firebase_tokens(db: AsyncSession, page: int = 1, limit: int = 10):
    try:
        offset = (page - 1) * limit if limit else 0
        query = select(FirebaseTokens)
        if limit:
            query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        firebase_tokens = result.scalars().all()

        count_query = select(func.count(FirebaseTokens.id))
        total = await db.scalar(count_query)

        return firebase_tokens, total or 0
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Firebase Tokens")
        raise e


async def get_firebase_token_by_id(db: AsyncSession, firebase_token_id: UUID):
    try:
        result = await db.execute(
            select(FirebaseTokens).where(FirebaseTokens.id == firebase_token_id)
        )
        return result.scalars().first()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Firebase Token")
        raise e


async def get_firebase_token_by_user_id(db: AsyncSession, user_id: UUID):
    try:
        result = await db.execute(
            select(FirebaseTokens).where(FirebaseTokens.user_id == user_id)
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not find Firebase Token by user id")
        raise e


async def create_firebase_token(db: AsyncSession, firebase_token: FirebaseTokens):
    try:
        db.add(firebase_token)
        await db.commit()
        await db.refresh(firebase_token)
        return firebase_token
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create Firebase Token")
        raise e


async def create_multiple_firebase_token(db: AsyncSession, firebase_tokens: list[FirebaseTokens]):
    try:
        db.add_all(firebase_tokens)
        await db.commit()
        return firebase_tokens
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not create Firebase Token")
        raise e


async def update_firebase_token(db: AsyncSession, update_data: dict, firebase_token_id: UUID):
    try:
        result = await db.execute(
            select(FirebaseTokens).where(FirebaseTokens.id == firebase_token_id)
        )
        db_firebase_token = result.scalars().first()

        if not db_firebase_token:
            return None

        for key, value in update_data.items():
            if key != "id":
                setattr(db_firebase_token, key, value)

        await db.commit()
        await db.refresh(db_firebase_token)
        return db_firebase_token
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not update Firebase Token")
        raise e


async def delete_firebase_token(db: AsyncSession, firebase_token_id: UUID):
    try:
        result = await db.execute(
            select(FirebaseTokens).where(FirebaseTokens.id == firebase_token_id)
        )
        db_firebase_token = result.scalars().first()
        if not db_firebase_token:
            return None
        await db.delete(db_firebase_token)
        await db.commit()
        return db_firebase_token
    except SQLAlchemyError as e:
        await db.rollback()
        logging.exception("Could not delete Firebase Token")
        raise e
