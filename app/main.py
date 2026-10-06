from fastapi import FastAPI
from app.routers.payments import router as payments_router


app = FastAPI()
app.include_router(payments_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
