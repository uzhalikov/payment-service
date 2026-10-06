from faststream.rabbit import RabbitBroker, RabbitQueue
from app.config import settings


broker = RabbitBroker(settings.rabbitmq_url)

payments_queue = RabbitQueue("payments.new", durable=True)

payments_retry_queue = RabbitQueue(
    "payments.retry",
    durable=True,
    arguments={
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": "payments.new"
    }
)

payments_dlq = RabbitQueue("payments.dlq", durable=True)
