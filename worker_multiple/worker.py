from celery import Celery
import os
import sys

sys.path.insert(0, os.path.split(os.getcwd())[0])

# RabbitMQ and Redis URIs
BROKER_URI = 'amqp://rabbitmq'
BACKEND_URI = 'redis://redis'

# Initialize Celery app
app = Celery(
    'worker_multiple',
    broker=BROKER_URI,
    backend=BACKEND_URI,
    include=['worker_multiple.tasks']
)

# Configure Celery app
app.conf.update(
    task_routes={
        'worker_multiple.tasks.head_generation': {'queue': 'queue1'},
        'worker_multiple.tasks.body_generation': {'queue': 'queue2'},
        'worker_multiple.tasks.task3': {'queue': 'queue3'},
    },
    task_queues={
        'queue1': {
            'exchange': 'default',
            'exchange_type': 'direct',
            'binding_key': 'queue1',
        },
        'queue2': {
            'exchange': 'default',
            'exchange_type': 'direct',
            'binding_key': 'queue2',
        },
        'queue3': {
            'exchange': 'default',
            'exchange_type': 'direct',
            'binding_key': 'queue3',
        },
    },
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',
    broker_connection_retry_on_startup=True,
)
