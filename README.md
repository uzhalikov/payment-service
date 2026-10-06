# Payment Service

Асинхронный сервис обработки платежей на FastAPI, PostgreSQL и RabbitMQ.

## Запуск

Требуется установленный Docker и Docker Compose.

1. Положить `.env` в корень проекта.
2. Запустить сервис командой `make up`.

Все запросы к сервису требуют HTTP-заголовок `X-API-Key` со значением из переменной `API_KEY` в файле `.env`.

## Примеры

### Создание платежа

```bash
curl -X POST http://localhost:8000/api/v1/payments \
  -H "X-API-Key: secret-key" \
  -H "Idempotency-Key: payment-001" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000.00,
    "currency": "RUB",
    "description": "Test payment",
    "metadata": {
      "order_id": 123
    },
    "webhook_url": "https://example.com/webhook"
  }'
```

### Получение платежа

```bash
curl http://localhost:8000/api/v1/payments/{payment_id} \
  -H "X-API-Key: secret-key"
```
