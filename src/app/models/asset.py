from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from src.app.database.db import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, nullable=False, unique=True, index=True)
    ip_address = Column(String, nullable=False, unique=True, index=True)
    url = Column(String, nullable=True)
    operating_system = Column(String, nullable=True)
    asset_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Unknown")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())