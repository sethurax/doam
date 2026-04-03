import os
import redis

db = redis.Redis(
    host=os.getenv("REDIS_HOST_PROD", ""),
    port=int(os.getenv("REDIS_PORT", "18224")),
    username=os.getenv("REDIS_UNAME", "default"),
    password=os.getenv("REDIS_PWD", "default"),
    db=0,
    decode_responses=True,
)
