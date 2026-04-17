.PHONY: dev test seed migrate lint format

# Start the FastAPI development server with hot reload
dev:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start the Streamlit dashboard
dashboard:
	streamlit run streamlit_app/app.py --server.port 8501

# Run all tests
test:
	cd backend && pytest tests/ -v --tb=short

# Run only unit tests (fast, no DB required)
test-unit:
	cd backend && pytest tests/unit/ -v --tb=short

# Seed the database with sample data
seed:
	python scripts/seed.py

# Run Alembic migrations
migrate:
	cd backend && alembic upgrade head

# Create a new Alembic migration (pass MSG="description")
migration:
	cd backend && alembic revision --autogenerate -m "$(MSG)"

# Run ruff linter
lint:
	cd backend && ruff check app/

# Auto-fix and format
format:
	cd backend && ruff format app/ && ruff check app/ --fix

# Start all services via Docker Compose
up:
	docker compose up --build

# Stop all services
down:
	docker compose down

# Tail backend logs
logs:
	docker compose logs -f backend
