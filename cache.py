import redis

HOST = '127.0.0.1'
PORT = 6379
DB = 1

connection_pool = redis.ConnectionPool(host=HOST, port=PORT, db=DB)
cache = redis.StrictRedis(connection_pool=connection_pool)
