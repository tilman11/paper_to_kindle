import os
import logging

import redis
from rq import Worker, Queue, Connection

# Create a logger for your application
worker_logger = logging.getLogger(__name__)

# Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
worker_logger.setLevel(logging.DEBUG)

# Create a file handler for logs (optional)
file_handler = logging.FileHandler('your_app.log')
file_handler.setLevel(logging.INFO)  # Set log level for file handler

# Define the format for log messages
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the handler to the logger (optional for file logging)
worker_logger.addHandler(file_handler)

listen = ['default']

redis_host = os.environ.get('REDIS_HOST', 'redis-pp')
redis_port = int(os.environ.get('REDIS_PORT', 6379))

worker_logger.info("Connecting to Host: %s", redis_host)
worker_logger.info("Connecting to Port: %i", redis_port)
conn_cli = redis.Redis(
    host=redis_host,
    port=redis_port,
    charset="utf-8",
    # decode_responses=True
    )

try:
    conn_test = conn_cli.ping()
    print(conn_test)
except ConnectionError as ce:
    worker_logger.error(ce)
    raise ce

if __name__ == '__main__':
    with Connection(conn_cli):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
