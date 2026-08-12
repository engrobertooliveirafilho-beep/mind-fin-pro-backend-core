import redis

r = redis.Redis()

def push(stream, data):
    r.xadd(stream, data)
