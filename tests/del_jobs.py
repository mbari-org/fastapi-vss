from rq import Worker, Queue
import redis

# redis_host="doris.shore.mbari.org"
# redis_port=6383
# password='KNLKpAmHqw9DuvPaWN6yhBWaCA'
# conn = redis.Redis(host=redis_host, port=redis_port, password=password)
# for queue in Queue.all(connection=conn):
#         queue.empty()

from rq import Worker, Queue
import redis

redis_host = "localhost"
redis_port = 6379
password = 'xvN2ErdyY4'
conn = redis.Redis(host=redis_host, port=redis_port, password=password)
for queue in Queue.all(connection=conn):
        queue.empty()