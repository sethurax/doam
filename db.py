import os

import redis
from dotenv import load_dotenv

load_dotenv()

redis_host = (
    os.getenv("REDIS_HOST_PROD", "")
    if os.name != "nt"
    else os.getenv("REDIS_HOST_DEV", "")
)
redis_port = 18224

r = redis.Redis(
    host=redis_host,
    port=redis_port,
    username=os.getenv("REDIS_UNAME", "default"),
    password=os.getenv("REDIS_PWD", "default"),
    db=0,
    decode_responses=True,
)


# Since all bot functionality relies on data stored in Redis, we test the Redis connection
# during startup and exit early if the connection fails.
def test_redis_connection(redis_client: redis.Redis):
    if redis_client.ping():
        return
    else:
        print("Redis connection failed.")
        exit(1)
