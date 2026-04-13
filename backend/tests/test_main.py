from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

import main


@dataclass
class DummyEvent:
    id: int
    title: str
    description: str | None
    date: datetime
    organizer: str | None
    address: str | None
    lat: float | None = None
    lng: float | None = None


class FakeDateRangeResult:
    def __init__(self, min_date, max_date):
        self._row = {"min_date": min_date, "max_date": max_date}

    def mappings(self):
        return self

    def first(self):
        return self._row


class FakeDB:
    def __init__(self, result=None):
        self.result = result
        self.queries = []

    async def execute(self, query):
        self.queries.append(query)
        return self.result


@pytest.mark.asyncio
async def test_list_events_parses_dates_and_returns_paginated_response(monkeypatch):
    fake_events = [
        DummyEvent(
            id=1,
            title="Festival: Cultura ciudadana",
            description="Descripción de prueba",
            date=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
            organizer="IDRD",
            address="Bogotá",
        )
    ]
    fake_get_events = AsyncMock(return_value=(1, fake_events))
    fake_cache_get = AsyncMock(return_value=None)
    fake_cache_set = AsyncMock()

    monkeypatch.setattr(main.crud, "get_events", fake_get_events)
    monkeypatch.setattr(main.cache, "get_cached", fake_cache_get)
    monkeypatch.setattr(main.cache, "set_cached", fake_cache_set)

    response = await main.list_events(
        page=2,
        size=10,
        from_date="2025-01-01",
        to_date="2025-01-31",
        db=FakeDB(),
    )

    fake_get_events.assert_awaited_once()
    called_db, called_page, called_size, called_from, called_to = fake_get_events.await_args.args

    assert called_page == 2
    assert called_size == 10
    assert called_from == datetime(2025, 1, 1, 0, 0)
    assert called_to == datetime(2025, 1, 31, 23, 59, 59, 999999)
    assert called_db is not None
    assert response.total == 1
    assert response.pages == 1
    assert response.results[0].title == "Festival: Cultura ciudadana"
    fake_cache_set.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_events_returns_cached_response_when_available(monkeypatch):
    cached = {
        "total": 5,
        "page": 1,
        "size": 10,
        "pages": 1,
        "results": [
            {
                "id": 1,
                "title": "Evento guardado",
                "date": "2025-01-01T12:00:00Z",
                "organizer": "IDRD",
                "address": "Bogotá",
            }
        ],
    }

    fake_get_events = AsyncMock()
    fake_cache_get = AsyncMock(return_value=cached)
    fake_cache_set = AsyncMock()

    monkeypatch.setattr(main.crud, "get_events", fake_get_events)
    monkeypatch.setattr(main.cache, "get_cached", fake_cache_get)
    monkeypatch.setattr(main.cache, "set_cached", fake_cache_set)

    response = await main.list_events(page=1, size=10, from_date=None, to_date=None, db=FakeDB())

    assert response == cached
    fake_get_events.assert_not_awaited()
    fake_cache_set.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_event_returns_detail_with_location(monkeypatch):
    fake_event = DummyEvent(
        id=10,
        title="Conferencia: Innovación pública",
        description="Detalle de prueba",
        date=datetime(2025, 2, 1, 9, 0, tzinfo=timezone.utc),
        organizer="Compensar",
        address="Corferias, Bogotá",
        lat=4.6,
        lng=-74.1,
    )
    fake_get_event = AsyncMock(return_value=fake_event)
    fake_cache_get = AsyncMock(return_value=None)
    fake_cache_set = AsyncMock()

    monkeypatch.setattr(main.crud, "get_event_by_id", fake_get_event)
    monkeypatch.setattr(main.cache, "get_cached", fake_cache_get)
    monkeypatch.setattr(main.cache, "set_cached", fake_cache_set)

    response = await main.get_event(event_id=10, db=FakeDB())

    assert response.id == 10
    assert response.location.address == "Corferias, Bogotá"
    assert response.location.lat == 4.6
    assert response.location.lng == -74.1
    fake_cache_set.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_event_raises_404_when_missing(monkeypatch):
    fake_get_event = AsyncMock(return_value=None)
    fake_cache_get = AsyncMock(return_value=None)

    monkeypatch.setattr(main.crud, "get_event_by_id", fake_get_event)
    monkeypatch.setattr(main.cache, "get_cached", fake_cache_get)

    with pytest.raises(HTTPException) as exc_info:
        await main.get_event(event_id=999, db=FakeDB())

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_events_date_range_returns_iso_strings():
    fake_db = FakeDB(FakeDateRangeResult(
        datetime(2025, 1, 1, 7, 0, tzinfo=timezone.utc),
        datetime(2027, 1, 1, 22, 15, tzinfo=timezone.utc),
    ))

    response = await main.get_events_date_range(db=fake_db)

    assert response == {
        "min_date": "2025-01-01T07:00:00+00:00",
        "max_date": "2027-01-01T22:15:00+00:00",
    }