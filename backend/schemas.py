from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class LocationSchema(BaseModel):
    lat:     Optional[float] = None
    lng:     Optional[float] = None
    address: Optional[str]   = None

class EventListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:        int
    title:     str
    date:      datetime
    organizer: Optional[str] = None
    address:   Optional[str] = None

class EventDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:          int
    title:       str
    description: Optional[str]      = None
    date:        datetime
    organizer:   Optional[str]      = None
    location:    Optional[LocationSchema] = None

    @classmethod
    def from_orm_with_location(cls, obj):
        return cls(
            id          = obj.id,
            title       = obj.title,
            description = obj.description,
            date        = obj.date,
            organizer   = obj.organizer,
            location    = LocationSchema(
                lat     = obj.lat,
                lng     = obj.lng,
                address = obj.address,
            ),
        )

class PaginatedEvents(BaseModel):
    total:    int
    page:     int
    size:     int
    pages:    int
    results:  list[EventListItem]