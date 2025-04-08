.PHONY: dev start test migrations migrate

# Command to start FastAPI server
dev:
	uvicorn main:app --reload

start:
	uvicorn main:app

# Command to run tests using pytest
test:
	coverage run -m pytest tests && coverage report -m

migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate
