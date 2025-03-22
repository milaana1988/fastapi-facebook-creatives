from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any


class CreativeBase(BaseModel):
    creative_id: str
    performance_metrics: Dict[str, Any]
    metadata: Dict[str, Any]
    image_url: str


class Creative(CreativeBase):
    id: int
    labels: Optional[List[str]] = []
    image_hash: Optional[str]

    class Config:
        orm_mode = True


class CreativeResponse(BaseModel):
    creative_id: int
    performance_metrics: Optional[Any] = None
    relevant_metadata: Optional[Any] = None
    image_url: Optional[str] = None
    labels: Optional[Any] = None
    image_hash: Optional[str] = None

    class Config:
        orm_mode = True


class PaginatedResponse(BaseModel):
    creative_details: List[CreativeResponse]
    has_more: bool
    next_cursor: Optional[int] = None


class Settings(BaseSettings):
    access_token: str
    api_version: str = "v22.0"
    client_id: str
    client_secret: str
    fb_api_url: str = "https://graph.facebook.com"
    db_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
