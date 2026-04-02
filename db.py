import os
import redis

# Using two separate DBs on the same Redis Cloud instance for development and production
branch = 0 if os.getenv("BRANCH") else 1

db = redis.Redis(
    host=os.getenv("REDIS_HOST_PROD", ""),
    port=18224,
    username=os.getenv("REDIS_UNAME", "default"),
    password=os.getenv("REDIS_PWD", "default"),
    db=branch,
    decode_responses=True,
)
