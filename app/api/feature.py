from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.user import User
from app.responses.base import BaseResponse
from app.responses.feature import (
    FeatureCreate,
    GetFeaturesResponse,
    GetFeatureResponse,
    CreateFeatureResponse,
    UpdateFeatureResponse,
)
from app.services.feature import (
    get_all_features_service,
    get_feature_service,
    create_feature_service,
    update_feature_service,
    delete_feature_service,
)
from app.core.security import require_permission

router = APIRouter(prefix="/features", tags=["Features"])


@router.get("", response_model=GetFeaturesResponse)
async def get_features(
    current_user: User = Depends(require_permission("features", "read")),
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    response = await get_all_features_service(db)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response.model_dump(mode="json")
    )


@router.get("/{id}", response_model=GetFeatureResponse)
async def get_feature(
    id: int,
    current_user: User = Depends(require_permission("features", "read")),
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    response = await get_feature_service(db, id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response.model_dump(mode="json")
    )


@router.post("", response_model=CreateFeatureResponse, status_code=status.HTTP_201_CREATED)
async def create_feature(
    feature_data: FeatureCreate,
    current_user: User = Depends(require_permission("features", "create")),
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    response = await create_feature_service(db, feature_data)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=response.model_dump(mode="json")
    )


@router.put("/{id}", response_model=UpdateFeatureResponse)
async def update_feature(
    id: int,
    feature_data: FeatureCreate,
    current_user: User = Depends(require_permission("features", "update")),
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    response = await update_feature_service(db, id, feature_data)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response.model_dump(mode="json")
    )


@router.delete("/{id}", response_model=BaseResponse)
async def delete_feature(
    id: int,
    current_user: User = Depends(require_permission("features", "delete")),
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    response = await delete_feature_service(db, id)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response.model_dump(mode="json")
    )
