from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Index
from sqlalchemy.sql import func
from database import Base

class Event(Base):
    __tablename__ = "events"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date        = Column(DateTime(timezone=True), nullable=False)
    address     = Column(String(500), nullable=True)
    lat         = Column(Float, nullable=True)
    lng         = Column(Float, nullable=True)
    organizer   = Column(String(255), nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

   
    __table_args__ = (
        Index("ix_events_date", "date"),                          # filtro por fecha
        Index("ix_events_date_id", "date", "id"),                 # paginación keyset
        Index("ix_events_title_trgm", "title",                    # búsqueda texto
              postgresql_ops={"title": "gin_trgm_ops"},
              postgresql_using="gin"),
    )