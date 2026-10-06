# Payment Service

Асинхронный сервис обработки платежей на FastAPI, PostgreSQL и RabbitMQ.

## Запуск

Требуется установленный Docker и Docker Compose.

1. Положить `.env` в корень проекта
2. Запустить сервис командой `make up`

Все запросы к сервису требуют HTTP заголовок X-API-Key со значением из переменной API_KEY в файле `.env`
