from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from datetime import datetime, time
from typing import Optional
import math, logging
from sqlalchemy import text

from database import engine, Base, get_db
from config   import settings
from models import Event
import crud, cache
from schemas  import PaginatedEvents, EventDetail, EventListItem, LocationSchema

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.run_sync(Base.metadata.create_all)
    await cache.init_redis(settings.REDIS_URL)
    yield
    # shutdown
    await engine.dispose()

app = FastAPI(
    title="Events Microservice",
    version="1.0.0",
    description="Módulo de eventos para app social",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# GET /events
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/events", response_model=PaginatedEvents, tags=["Events"])
async def list_events(
    page:      int            = Query(1,    ge=1),
    size:      int            = Query(10,   ge=1, le=100),
    from_date: Optional[str]  = Query(None, alias="from",
                                      description="Fecha inicio YYYY-MM-DD"),
    to_date:   Optional[str]  = Query(None, alias="to",
                                      description="Fecha fin YYYY-MM-DD"),
    db:        AsyncSession   = Depends(get_db),
):
    # parse fechas
    dt_from = datetime.combine(datetime.fromisoformat(from_date).date(), time.min) if from_date else None
    dt_to   = datetime.combine(datetime.fromisoformat(to_date).date(), time.max) if to_date else None

    cache_key = cache.build_key("list", page, size, from_date, to_date)
    cached    = await cache.get_cached(cache_key)
    if cached:
        return cached

    total, events = await crud.get_events(db, page, size, dt_from, dt_to)
    pages = math.ceil(total / size) if total else 0

    response = PaginatedEvents(
        total   = total,
        page    = page,
        size    = size,
        pages   = pages,
        results = [EventListItem.model_validate(e) for e in events],
    )

    await cache.set_cached(cache_key, response.model_dump(), ttl=settings.CACHE_TTL)
    return response


# ─────────────────────────────────────────────────────────────────────────────
# GET /events/date-range
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/events/date-range", tags=["Events"])
async def get_events_date_range(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT MIN(date) AS min_date, MAX(date) AS max_date FROM events")
    )
    row = result.mappings().first() or {}
    return {
        "min_date": row.get("min_date").isoformat() if row.get("min_date") else None,
        "max_date": row.get("max_date").isoformat() if row.get("max_date") else None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /events/{id}
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/events/{event_id}", response_model=EventDetail, tags=["Events"])
async def get_event(
    event_id: int,
    db:       AsyncSession = Depends(get_db),
):
    cache_key = cache.build_key("detail", event_id)
    cached    = await cache.get_cached(cache_key)
    if cached:
        return cached

    event = await crud.get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    response = EventDetail.from_orm_with_location(event)
    await cache.set_cached(cache_key, response.model_dump(), ttl=settings.CACHE_TTL)
    return response


# ─────────────────────────────────────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "service": "events-microservice"}