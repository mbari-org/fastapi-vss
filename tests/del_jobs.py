from rq import Queue
import redis

redis_host = "localhost"
redis_port = 6379
password = "xvN2ErdyY4"
conn = redis.Redis(host=redis_host, port=redis_port, password=password)
for queue in Queue.all(connection=conn):
    queue.empty()
