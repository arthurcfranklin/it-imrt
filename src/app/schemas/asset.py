from pydantic import BaseModel


class AssetCreate(BaseModel):
    hostname: str
    ip_address: str
    url: str | None = None
    operating_system: str
    asset_type: str
    status: str


class AssetResponse(AssetCreate):
    id: int

    class Config:
        from_attributes = True