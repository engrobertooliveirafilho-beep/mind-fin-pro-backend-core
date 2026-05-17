import os

from app.eldora.core.true_redis_runtime import redis_client

def redis_diagnostics():

    url = os.getenv("REDIS_URL")

    info = {
        "status": "ok",
        "redis_url_present": bool(url),
        "redis_url_scheme": url.split("://")[0] if url and "://" in url else None,
        "redis_client_created": False,
        "ping": False,
        "error": None
    }

    try:

        client = redis_client()

        info["redis_client_created"] = client is not None

        if client:

            info["ping"] = bool(client.ping())

    except Exception as e:

        info["error"] = str(e)

    return info
