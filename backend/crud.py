from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime
from typing import Optional
from models import Event

async def get_events(
    db:        AsyncSession,
    page:      int           = 1,
    size:      int           = 10,
    from_date: Optional[datetime] = None,
    to_date:   Optional[datetime] = None,
):
    size  = min(size, 100)      # límite
    offset = (page - 1) * size

    filters = []
    if from_date:
        filters.append(Event.date >= from_date)
    if to_date:
        filters.append(Event.date <= to_date)

    where = and_(*filters) if filters else True

    # total
    total_q = await db.execute(select(func.count()).select_from(Event).where(where))
    total   = total_q.scalar_one()

    # resultados paginados — usa índice ix_events_date
    q = (
        select(Event)
        .where(where)
        .order_by(Event.date.asc(), Event.id.asc())
        .offset(offset)
        .limit(size)
    )
    result = await db.execute(q)
    events = result.scalars().all()

    return total, events

async def get_event_by_id(db: AsyncSession, event_id: int) -> Optional[Event]:
    result = await db.execute(select(Event).where(Event.id == event_id))
    return result.scalar_one_or_none()