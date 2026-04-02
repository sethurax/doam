import os
import redis

# Using two separate DBs on one Redis instance for production and development
branch = 0 if os.getenv("BRANCH") == "main" else 1

db = redis.Redis(
    host=os.getenv("REDIS_HOST_PROD", ""),
    port=18224,
    username=os.getenv("REDIS_UNAME", "default"),
    password=os.getenv("REDIS_PWD", "default"),
    db=branch,
    decode_responses=True,
)
