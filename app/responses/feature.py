from datetime import datetime
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.responses.base import BaseResponse

class FeatureBase(BaseModel):
    feature_key: str
    display_name: str
    description: str | None = None
    parent_feature_id: UUID | None = None

    model_config = ConfigDict(from_attributes=True)

class FeatureCreate(FeatureBase):
    pass

class FeatureRead(FeatureBase):
    feature_id: UUID
    created_at: datetime
    updated_at: datetime

class GetFeaturesResponse(BaseResponse):
    features: list[FeatureRead]

class GetFeatureResponse(BaseResponse):
    feature: FeatureRead

class CreateFeatureResponse(BaseResponse):
    feature: FeatureRead

class UpdateFeatureResponse(BaseResponse):
    feature: FeatureRead
