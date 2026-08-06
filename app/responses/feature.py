from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.responses.base import BaseResponse

class FeatureBase(BaseModel):
    feature_key: str
    display_name: str
    description: str | None = None
    parent_feature_id: int | None = None

    model_config = ConfigDict(from_attributes=True)

class FeatureCreate(FeatureBase):
    pass

class FeatureRead(FeatureBase):
    feature_id: int
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
