import redis, json, uuid

r = redis.Redis(host='localhost', port=6379)

def push(job):
    job['id'] = str(uuid.uuid4())
    r.lpush('eldora_jobs', json.dumps(job))
    return job['id']
