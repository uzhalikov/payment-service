up:
	docker compose up --build -d
	docker compose exec api alembic upgrade head
