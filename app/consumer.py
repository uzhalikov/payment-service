import asyncio
import logging
import random
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import UUID

import httpx
from faststream import FastStream
from faststream.rabbit import RabbitMessage
from sqlalchemy import select

from app.broker import broker, payments_dlq, payments_queue, payments_retry_queue
from app.database import async_session
from app.models import Payment, PaymentStatus
from app.services.outbox import outbox_worker

logger = logging.getLogger(__name__)


async def send_webhook(payment: Payment):
    async with httpx.AsyncClient() as client:
        for attempt in range(3):
            try:
                response = await client.post(
                    payment.webhook_url,
                    json={
                        "payment_id": str(payment.id),
                        "status": payment.status
                    }
                )
                response.raise_for_status()
                return
            except httpx.HTTPError as error:
                logger.warning(f"Webhook attempt {attempt + 1} failed for payment {payment.id}: {error}")

                if attempt == 2:
                    logger.error(f"Webhook delivery failed for payment {payment.id} after 3 attempts")
                    raise

                await asyncio.sleep(2 ** attempt)


@broker.subscriber(payments_queue)
async def process_payment(message: dict, msg: RabbitMessage):
    retry_count = int(msg.headers.get("x-retry-count", 0))

    try:
        payment_id = UUID(message["payment_id"])

        async with async_session() as session:
            payment = await session.scalar(select(Payment).where(Payment.id == payment_id))

            if not payment:
                return

            await asyncio.sleep(random.uniform(2, 5))

            payment.status = PaymentStatus.SUCCEEDED if random.random() < 0.9 else PaymentStatus.FAILED
            payment.processed_at = datetime.now(timezone.utc)

            await session.commit()

            try:
                await send_webhook(payment)
            except Exception:
                pass

    except Exception as error:
        logger.error(f"Payment processing failed, attempt {retry_count + 1}: {error}")

        if retry_count >= 2:
            await broker.publish(
                message,
                queue=payments_dlq,
                headers={"x-retry-count": retry_count},
            )
            logger.error("Payment message moved to DLQ")
            return

        retry_count += 1

        await broker.publish(
            message,
            queue=payments_retry_queue,
            headers={"x-retry-count": retry_count},
            expiration=2 ** (retry_count - 1)
        )


@asynccontextmanager
async def lifespan():
    task = asyncio.create_task(outbox_worker())
    yield
    task.cancel()


app = FastStream(broker, lifespan=lifespan)

@app.after_startup
async def declare_queues():
    await broker.declare_queue(payments_retry_queue)
    await broker.declare_queue(payments_dlq)


if __name__ == "__main__":
    asyncio.run(app.run())
