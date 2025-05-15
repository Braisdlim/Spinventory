import redis
from config import Config

r = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    decode_responses=False
)

print("Claves en Redis:")
for key in r.keys():
    print("-", key)
    if r.type(key) == b'hash':
        print("  Campos:", list(r.hkeys(key)))