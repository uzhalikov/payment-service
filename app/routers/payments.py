from uuid import UUID
from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import PaymentCreate, PaymentCreateResponse, PaymentResponse
from app.services import payments
from app.dependencies import verify_api_key, get_session

router = APIRouter(prefix="/api/v1/payments", dependencies=[Depends(verify_api_key)])


@router.post(
    "",
    response_model=PaymentCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={status.HTTP_409_CONFLICT: {"description": "Idempotency key is already used"}}
)
async def create_payment(
    data: PaymentCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    session: AsyncSession = Depends(get_session),
):
    payment = await payments.create_payment(session=session, data=data, idempotency_key=idempotency_key)
    return PaymentCreateResponse(payment_id=payment.id, status=payment.status, created_at=payment.created_at)


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Payment not found"}}
)
async def get_payment(payment_id: UUID, session: AsyncSession = Depends(get_session)):
    payment = await payments.get_payment(session=session, payment_id=payment_id)
    return PaymentResponse.model_validate(payment)
