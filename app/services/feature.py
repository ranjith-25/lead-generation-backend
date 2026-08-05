from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.responses.feature import (
    FeatureCreate,
    FeatureRead,
    GetFeaturesResponse,
    GetFeatureResponse,
    CreateFeatureResponse,
    UpdateFeatureResponse,
)
from app.responses.base import BaseResponse
from app.models.feature import Feature
from app.services.db.feature import (
    get_feature_by_id_db,
    get_feature_by_key_db,
    get_all_features_db,
    add_feature_db,
    update_feature_db,
    delete_feature_db,
)

async def get_all_features_service(db: AsyncSession) -> GetFeaturesResponse:
    features = await get_all_features_db(db)
    features_read = [FeatureRead.model_validate(f) for f in features]
    return GetFeaturesResponse(
        message="Features fetched successfully",
        features=features_read
    )

async def get_feature_service(db: AsyncSession, feature_id: int | str) -> GetFeatureResponse:
    try:
        parsed_id = int(feature_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid Feature ID format")

    feature = await get_feature_by_id_db(db, parsed_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    return GetFeatureResponse(
        message="Feature fetched successfully",
        feature=FeatureRead.model_validate(feature)
    )

async def create_feature_service(db: AsyncSession, feature_data: FeatureCreate) -> CreateFeatureResponse:
    existing = await get_feature_by_key_db(db, feature_data.feature_key)
    if existing:
        raise HTTPException(status_code=400, detail="Feature with this key already exists")

    if feature_data.parent_feature_id is not None:
        parent = await get_feature_by_id_db(db, feature_data.parent_feature_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent feature not found")

    feature_dict = feature_data.model_dump()
    new_feature = Feature(**feature_dict)
    saved_feature = await add_feature_db(db, new_feature)
    return CreateFeatureResponse(
        message="Feature created successfully",
        feature=FeatureRead.model_validate(saved_feature)
    )

async def update_feature_service(
    db: AsyncSession, feature_id: int | str, feature_data: FeatureCreate
) -> UpdateFeatureResponse:
    try:
        parsed_id = int(feature_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid Feature ID format")

    feature = await get_feature_by_id_db(db, parsed_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    if feature_data.feature_key != feature.feature_key:
        existing = await get_feature_by_key_db(db, feature_data.feature_key)
        if existing:
            raise HTTPException(status_code=400, detail="Feature with this key already exists")

    if feature_data.parent_feature_id is not None:
        if feature_data.parent_feature_id == parsed_id:
            raise HTTPException(status_code=400, detail="A feature cannot be its own parent")
        parent = await get_feature_by_id_db(db, feature_data.parent_feature_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent feature not found")

    update_dict = feature_data.model_dump(exclude_unset=True)
    updated_feature = await update_feature_db(db, feature, update_dict)
    return UpdateFeatureResponse(
        message="Feature updated successfully",
        feature=FeatureRead.model_validate(updated_feature)
    )

async def delete_feature_service(db: AsyncSession, feature_id: int | str) -> BaseResponse:
    try:
        parsed_id = int(feature_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid Feature ID format")

    feature = await get_feature_by_id_db(db, parsed_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")

    await delete_feature_db(db, feature)
    return BaseResponse(message="Feature deleted successfully")
