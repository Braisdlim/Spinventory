import redis
from config import Config

def test_redis_connection():
    r = redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DB
    )
    try:
        r.ping()
        print("✅ Conexión a Redis exitosa!")
        return True
    except redis.ConnectionError:
        print("❌ No se pudo conectar a Redis")
        return False

if __name__ == '__main__':
    test_redis_connection()