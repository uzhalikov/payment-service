import asyncio
from datetime import datetime, timezone
from sqlalchemy import select
from app.broker import broker, payments_queue
from app.database import async_session
from app.models import Outbox


async def publish_outbox_events():
    async with async_session() as session:
        events = await session.scalars(
            select(Outbox)
            .where(Outbox.published_at.is_(None))
            .order_by(Outbox.created_at)
        )

        for event in events:
            await broker.publish(event.payload, queue=payments_queue)
            event.published_at = datetime.now(timezone.utc)
        await session.commit()


async def outbox_worker():
    while True:
        await publish_outbox_events()
        await asyncio.sleep(1)
