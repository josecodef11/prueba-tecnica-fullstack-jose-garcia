# Prueba técnica fullstack

Proyecto con backend en FastAPI, base de datos PostgreSQL, caché en Redis y frontend en PHP.

## Requisitos

- Docker y Docker Compose
- Python 3.11 si se va  a correr el backend en local

## Levantar con Docker Compose

-ejecutar docker

en la terminal desde el proyecto

```bash
docker compose up --build
```
para generar los eventos 
```bash
 docker compose exec backend python seed.py
```
Servicios expuestos:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8080`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Levantar en local

1. Crear y activar el entorno virtual:

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Instalar dependencias del backend:

```bash
pip install -r backend/requirements.txt
```

3. Configurar variables de entorno.


```env
DATABASE_URL=postgresql+asyncpg://events_user:events_pass@localhost:5432/events_db
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300
APP_ENV=development
```

4. Iniciar el servidor:

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Ejecutar pruebas

Desde la raíz del repositorio:

```bash
python -m pytest backend/tests
```

Deuda técnica

Se gestionaría bajo un criterio de priorización por criticidad, impacto y riesgo: atendiendo primero lo que comprometa pruebas, despliegue o integridad de datos, separando refactorizaciones de cambios funcionales, documentando toda deuda con prioridad y alcance, priorizando lo que afecte mantenibilidad, observabilidad o seguridad y reservando capacidad periódica para su reducción progresiva.