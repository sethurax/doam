import os

import redis
from dotenv import load_dotenv

load_dotenv()

db = redis.Redis(
    host=os.getenv("REDIS_HOST_PROD", ""),
    port=18224,
    username=os.getenv("REDIS_UNAME", "default"),
    password=os.getenv("REDIS_PWD", "default"),
    db=0,
    decode_responses=True,
)
