"""
Genera eventos de prueba en la base de datos.
Ejecutar: python seed.py
  --count 30000   # opción para cambiar cantidad
  --force         # borra los eventos existentes antes de generar
"""
import argparse
import asyncio
import random
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy import delete, select, func

from database import engine, Base, AsyncSessionLocal
from models import Event

fake = Faker("es_CO")

LOCATIONS = [
    {"address": "Parque Simón Bolívar, Bogotá",   "lat": 4.658, "lng": -74.096},
    {"address": "Plaza de Bolívar, Bogotá",       "lat": 4.598, "lng": -74.076},
    {"address": "Estadio El Campín, Bogotá",      "lat": 4.646, "lng": -74.077},
    {"address": "Centro Comercial Andino, Bogotá","lat": 4.667, "lng": -74.053},
    {"address": "Corferias, Bogotá",              "lat": 4.628, "lng": -74.103},
    {"address": "Teatro Colón, Bogotá",           "lat": 4.597, "lng": -74.074},
    {"address": "Jardín Botánico, Bogotá",        "lat": 4.660, "lng": -74.099},
    {"address": "La Candelaria, Bogotá",          "lat": 4.596, "lng": -74.072},
]

ORGANIZERS = [
    "IDRD",
    "Alcaldía de Bogotá",
    "Cámara de Comercio de Bogotá",
    "Universidad Nacional",
    "Compensar",
    "Maloka",
    "Corferias",
    "Secretaría de Cultura",
]

EVENT_TYPES = [
    "Conferencia",
    "Feria",
    "Concierto",
    "Festival",
    "Taller",
    "Networking",
    "Exposición",
    "Seminario",
]

TOPICS = [
    "innovación pública",
    "emprendimiento local",
    "tecnología cívica",
    "formación profesional",
    "cultura ciudadana",
    "movilidad urbana",
    "salud comunitaria",
    "economía creativa",
]

DESCRIPTION_TEMPLATES = [
    "Este evento reúne a personas interesadas en {topic} para compartir ideas y experiencias.",
    "La jornada está pensada para fortalecer redes de trabajo y promover soluciones prácticas.",
    "Habrá espacio para preguntas, demostraciones y conversación abierta con los asistentes.",
    "La actividad se desarrolla en un ambiente cercano y enfocado en resultados útiles para la comunidad.",
]


def build_title(event_type: str) -> str:
    return f"{event_type}: {random.choice(TOPICS).capitalize()}"


def build_description() -> str:
    sentences = []
    for template in DESCRIPTION_TEMPLATES:
        sentences.append(template.format(topic=random.choice(TOPICS)))
    return " ".join(sentences)

async def seed(count: int = 30000, force: bool = False):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(func.count()).select_from(Event))
        existing = result.scalar_one()

        if existing and not force:
            print(f"Ya existen {existing} eventos en la base de datos. No se ejecuta seed.")
            return

        if existing and force:
            print("Borrando eventos existentes...")
            await db.execute(delete(Event))
            await db.commit()

        print(f"Generando {count:,} eventos...")

        batch = []
        batch_size = 1000
        base_date = datetime(2025, 1, 1)

        for i in range(count):
            loc = random.choice(LOCATIONS)
            event_type = random.choice(EVENT_TYPES)

            event = Event(
                title=build_title(event_type),
                description=build_description(),
                date=base_date + timedelta(
                    days=random.randint(0, 730),
                    hours=random.randint(7, 22),
                    minutes=random.choice([0, 15, 30, 45]),
                ),
                organizer=random.choice(ORGANIZERS),
                address=loc["address"],
                lat=loc["lat"] + random.uniform(-0.01, 0.01),
                lng=loc["lng"] + random.uniform(-0.01, 0.01),
            )

            batch.append(event)

            if len(batch) >= batch_size:
                db.add_all(batch)
                await db.commit()
                batch.clear()
                print(f"Insertados {i + 1} eventos...")

        if batch:
            db.add_all(batch)
            await db.commit()

        print("Seed completado ✓")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Seed de eventos')
    parser.add_argument('--count', type=int, default=30000, help='Cantidad de eventos a generar')
    parser.add_argument('--force', action='store_true', help='Borrar eventos existentes antes de generar')
    args = parser.parse_args()

    asyncio.run(seed(count=args.count, force=args.force))