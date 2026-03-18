#!/usr/bin/env python3
"""Aegis Background Worker - processes async jobs from Redis queue."""

import os
import json
import time
import uuid
import logging
import requests

import redis

logging.basicConfig(level=logging.INFO, format="%(asctime)s [worker] %(message)s")
log = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
AGENT_URL = os.getenv("AGENT_URL", "http://agent:8000")
QUEUE_KEY = "aegis:jobs"
RESULT_TTL = 3600  # seconds


def get_redis() -> redis.Redis:
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD or None,
        decode_responses=True,
    )


def process_job(r: redis.Redis, job: dict):
    job_id = job.get("job_id", str(uuid.uuid4()))
    message = job.get("message", "")
    user_id = job.get("user_id", "default_user")
    session_id = job.get("session_id", str(uuid.uuid4()))

    log.info("Processing job %s: %.80s", job_id, message)

    result_key = f"aegis:result:{job_id}"
    try:
        resp = requests.post(
            f"{AGENT_URL}/chat",
            json={"message": message, "user_id": user_id, "session_id": session_id},
            timeout=60,
        )
        resp.raise_for_status()
        result = {"status": "ok", "job_id": job_id, **resp.json()}
    except Exception as e:
        log.error("Job %s failed: %s", job_id, e)
        result = {"status": "error", "job_id": job_id, "error": str(e)}

    r.setex(result_key, RESULT_TTL, json.dumps(result))
    log.info("Job %s done → %s", job_id, result.get("status"))


def run():
    log.info("Connecting to Redis at %s:%s", REDIS_HOST, REDIS_PORT)
    r = get_redis()
    log.info("Worker ready — listening on queue '%s'", QUEUE_KEY)

    while True:
        try:
            item = r.blpop(QUEUE_KEY, timeout=5)
            if item:
                _, raw = item
                job = json.loads(raw)
                process_job(r, job)
        except redis.exceptions.ConnectionError as e:
            log.warning("Redis connection lost: %s — retrying in 5s", e)
            time.sleep(5)
        except Exception as e:
            log.error("Unexpected error: %s", e)
            time.sleep(1)


if __name__ == "__main__":
    run()
