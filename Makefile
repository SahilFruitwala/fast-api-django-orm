.PHONY: run test

# Command to start FastAPI server
dev:
	uvicorn main:app --reload

start:
	uvicorn main:app --reload

# Command to run tests using pytest
test:
	coverage run -m pytest tests && coverage report -m
