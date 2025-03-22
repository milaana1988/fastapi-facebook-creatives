from sqlalchemy import Column, Integer, String, Text, BigInteger
from sqlalchemy.types import JSON
from app.database import Base


class Creative(Base):
    __tablename__ = "creatives"
    id = Column(Integer, primary_key=True, index=True)
    creative_id = Column(BigInteger, unique=True, index=True)
    performance_metrics = Column(JSON().with_variant(Text, "mssql"))
    relevant_metadata = Column(JSON().with_variant(Text, "mssql"))
    image_url = Column(String)
    labels = Column(JSON().with_variant(Text, "mssql"))
    image_hash = Column(String(255), unique=True, nullable=True)
