import os

import redis
from rq import Worker, Queue, Connection

listen = ['default']

redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = int(os.environ.get('REDIS_PORT', 6379))

conn_cli = redis.Redis(
    host=redis_host,
    port=redis_port,
    charset="utf-8", #'utf-8'
    # decode_responses=True
    )


conn_test = conn_cli.ping()
print(conn_test)

if __name__ == '__main__':
    with Connection(conn_cli):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
