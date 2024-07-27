import os
from celery import Celery
import sys

sys.path.insert(0, os.path.split(os.getcwd())[0])

BROKER_URI = 'amqp://rabbitmq'
BACKEND_URI = 'redis://redis'

app = Celery(
    'worker',
    broker=BROKER_URI,
    backend=BACKEND_URI,
    include=['worker.tasks']
)
app.conf.update(
    broker_connection_retry_on_startup=True,
)