"""
Cache de dos niveles:
  1. In-memory
  2. Redis      
"""
import json, time, hashlib, logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ── Cache en memoria ─────────────────────────────────────────────────────────
_memory_cache: dict[str, tuple[Any, float]] = {}

def _mem_get(key: str) -> Optional[Any]:
    entry = _memory_cache.get(key)
    if entry and time.time() < entry[1]:
        return entry[0]
    _memory_cache.pop(key, None)
    return None

def _mem_set(key: str, value: Any, ttl: int):
    _memory_cache[key] = (value, time.time() + ttl)

# Redis
_redis_client = None

async def init_redis(url: str):
    global _redis_client
    try:
        import redis.asyncio as aioredis
        _redis_client = aioredis.from_url(url, decode_responses=True)
        await _redis_client.ping()
        logger.info("Redis cache conectado ✓")
    except Exception as e:
        logger.warning(f"Redis no disponible {e}")
        _redis_client = None

def build_key(*parts) -> str:
    raw = ":".join(str(p) for p in parts)
    return "events:" + hashlib.md5(raw.encode()).hexdigest()

async def get_cached(key: str) -> Optional[Any]:
    # 1. memoria
    val = _mem_get(key)
    if val is not None:
        return val
    # 2. redis
    if _redis_client:
        try:
            raw = await _redis_client.get(key)
            if raw:
                val = json.loads(raw)
                _mem_set(key, val, 60)   # warm up memoria
                return val
        except Exception:
            pass
    return None

async def set_cached(key: str, value: Any, ttl: int = 300):
    _mem_set(key, value, min(ttl, 60))
    if _redis_client:
        try:
            await _redis_client.setex(key, ttl, json.dumps(value, default=str))
        except Exception:
            pass

async def invalidate(pattern: str = "events:*"):
    _memory_cache.clear()
    if _redis_client:
        try:
            keys = await _redis_client.keys(pattern)
            if keys:
                await _redis_client.delete(*keys)
        except Exception:
            pass