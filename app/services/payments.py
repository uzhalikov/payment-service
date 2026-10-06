from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Outbox, Payment
from app.schemas import PaymentCreate


async def create_payment(session: AsyncSession, data: PaymentCreate, idempotency_key: str) -> Payment:
    existing_payment = await session.scalar(select(Payment).where(Payment.idempotency_key == idempotency_key))

    if existing_payment:
        raise HTTPException(status.HTTP_409_CONFLICT, "Idempotency key is already used")

    payment = Payment(
        amount=data.amount,
        currency=data.currency,
        description=data.description,
        payment_metadata=data.payment_metadata,
        idempotency_key=idempotency_key,
        webhook_url=str(data.webhook_url)
    )

    session.add(payment)
    await session.flush()

    outbox = Outbox(event_type="payment.created", payload={"payment_id": str(payment.id)})

    session.add(outbox)
    await session.commit()
    return payment


async def get_payment(session: AsyncSession, payment_id: UUID) -> Payment:
    payment = await session.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Payment not found")
    return payment
