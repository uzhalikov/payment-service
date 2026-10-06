up:
	docker compose up --build -d
	docker compose exec api alembic upgrade head

destroy:
	docker compose down --rmi all -v
