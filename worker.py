import redis
from rq import Worker, Queue, Connection

listen = ['default']

conn_cli = redis.Redis(
    host='localhost',
    port=6379,
    charset="utf-8", #'utf-8'
    # decode_responses=True
    )


conn_test = conn_cli.ping()
print(conn_test)

if __name__ == '__main__':
    with Connection(conn_cli):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
