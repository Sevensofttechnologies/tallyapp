"""Redis Queue Helpers

Minimal Redis helpers for enqueue/dequeue of export jobs.

This is intentionally small and dependency-light so we can later swap to a
full job framework (ARQ/RQ/Celery) without rewriting API endpoints.
"""

import json
import socket
import time
from typing import Any, Dict, List, Optional

import redis

from app.config import settings


def get_redis_client() -> redis.Redis:
    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def _now_iso() -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def _heartbeat_key(worker_type: str) -> str:
    host = socket.gethostname()
    return f"tallybridge:workers:{worker_type}:{host}:heartbeat"


def set_worker_heartbeat(worker_type: str, ttl_seconds: int = 60) -> None:
    client = get_redis_client()
    client.setex(_heartbeat_key(worker_type), int(ttl_seconds), _now_iso())


def workers_status() -> List[Dict[str, Any]]:
    client = get_redis_client()
    keys = list(client.scan_iter(match="tallybridge:workers:*:heartbeat"))
    items: List[Dict[str, Any]] = []
    for k in sorted(keys):
        ttl = client.ttl(k)
        last_seen = client.get(k)
        parts = k.split(':')
        worker_type = parts[2] if len(parts) >= 5 else "unknown"
        host = parts[3] if len(parts) >= 5 else "unknown"
        items.append(
            {
                "worker": worker_type,
                "host": host,
                "status": "ALIVE" if (ttl and ttl > 0) else "DEAD",
                "ttl": ttl,
                "last_seen": last_seen,
            }
        )
    return items


def redis_info() -> Dict[str, Any]:
    client = get_redis_client()
    info = client.info()  # type: ignore[attr-defined]
    return {
        "url": settings.REDIS_URL,
        "redis_version": info.get("redis_version"),
        "connected_clients": info.get("connected_clients"),
        "used_memory_human": info.get("used_memory_human"),
        "uptime_in_seconds": info.get("uptime_in_seconds"),
    }


def get_queue_lengths() -> Dict[str, int]:
    client = get_redis_client()
    return {
        settings.EMAIL_JOBS_QUEUE_NAME: int(client.llen(settings.EMAIL_JOBS_QUEUE_NAME)),
        settings.EXPORT_JOBS_QUEUE_NAME: int(client.llen(settings.EXPORT_JOBS_QUEUE_NAME)),
    }


def peek_queue(queue_name: str, side: str = "tail", count: int = 20) -> List[Dict[str, Any]]:
    client = get_redis_client()
    count = max(1, min(int(count), 200))
    if side == "head":
        raw_items = client.lrange(queue_name, 0, count - 1)
    else:
        raw_items = client.lrange(queue_name, -count, -1)
    out: List[Dict[str, Any]] = []
    for raw in raw_items:
        try:
            out.append(json.loads(raw))
        except Exception:
            out.append({"raw": raw})
    return out


def purge_queue(queue_name: str, mode: str = "all", count: int = 0) -> int:
    client = get_redis_client()
    removed = 0

    if mode == "all":
        removed = int(client.llen(queue_name))
        client.delete(queue_name)
        return removed

    n = max(0, int(count))
    if n <= 0:
        return 0

    # "oldest" depends on how we push jobs today:
    # - email_jobs: LPUSH; BRPOP pops tail; so oldest are at tail.
    # - export_jobs: RPUSH; BRPOP pops tail; so oldest are at head.
    if queue_name == settings.EMAIL_JOBS_QUEUE_NAME:
        for _ in range(n):
            if client.rpop(queue_name) is None:
                break
            removed += 1
    else:
        for _ in range(n):
            if client.lpop(queue_name) is None:
                break
            removed += 1
    return removed


def _dlq_key(dlq_type: str) -> str:
    return f"tallybridge:dlq:{dlq_type}"


def dlq_push(dlq_type: str, item: Dict[str, Any]) -> None:
    client = get_redis_client()
    client.lpush(_dlq_key(dlq_type), json.dumps(item))


def dlq_peek(dlq_type: str, count: int = 20) -> List[Dict[str, Any]]:
    client = get_redis_client()
    raw_items = client.lrange(_dlq_key(dlq_type), 0, max(0, int(count) - 1))
    out: List[Dict[str, Any]] = []
    for raw in raw_items:
        try:
            out.append(json.loads(raw))
        except Exception:
            out.append({"raw": raw})
    return out


def dlq_requeue_one(dlq_type: str, index: int) -> int:
    client = get_redis_client()
    key = _dlq_key(dlq_type)
    raw = client.lindex(key, index)
    if raw is None:
        return 0
    client.lrem(key, 1, raw)

    try:
        item = json.loads(raw)
    except Exception:
        item = {"raw": raw}

    if dlq_type == "email":
        client.lpush(settings.EMAIL_JOBS_QUEUE_NAME, json.dumps(item))
    else:
        client.rpush(settings.EXPORT_JOBS_QUEUE_NAME, json.dumps(item))
    return 1


def dlq_delete_one(dlq_type: str, index: int) -> int:
    client = get_redis_client()
    key = _dlq_key(dlq_type)
    raw = client.lindex(key, index)
    if raw is None:
        return 0
    client.lrem(key, 1, raw)
    return 1


def _inflight_key(queue_name: str) -> str:
    return f"tallybridge:inflight:{queue_name}"


def inflight_add(queue_name: str, job_id: str, ttl_seconds: int = 900) -> None:
    client = get_redis_client()
    client.hset(_inflight_key(queue_name), job_id, _now_iso())
    client.expire(_inflight_key(queue_name), int(ttl_seconds))


def inflight_remove(queue_name: str, job_id: str) -> None:
    client = get_redis_client()
    client.hdel(_inflight_key(queue_name), job_id)


def enqueue_export_job(job_id: int, payload: Optional[Dict[str, Any]] = None) -> None:
    client = get_redis_client()
    message = {
        "job_id": job_id,
        "payload": payload or {},
    }
    client.rpush(settings.EXPORT_JOBS_QUEUE_NAME, json.dumps(message))


def dequeue_export_job(timeout: int = 5) -> Optional[Dict[str, Any]]:
    client = get_redis_client()
    item = client.brpop(settings.EXPORT_JOBS_QUEUE_NAME, timeout=timeout)
    if not item:
        return None
    _, raw = item
    try:
        return json.loads(raw)
    except Exception:
        return {"job_id": None, "payload": {}, "raw": raw}


def enqueue_email_job(audit_id: int, payload: Dict[str, Any]) -> None:
    client = get_redis_client()
    item = {
        "audit_id": audit_id,
        "payload": payload,
    }
    client.lpush(settings.EMAIL_JOBS_QUEUE_NAME, json.dumps(item))


def dequeue_email_job(timeout: int = 5) -> Optional[Dict[str, Any]]:
    client = get_redis_client()
    item = client.brpop(settings.EMAIL_JOBS_QUEUE_NAME, timeout=timeout)
    if not item:
        return None
    _, raw = item
    try:
        return json.loads(raw)
    except Exception:
        return {"audit_id": None, "payload": {}, "raw": raw}
