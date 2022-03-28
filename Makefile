venv:
	python3 -m venv venv && python3 -m pip install -r requirements.txt && python3 -m pip install -r requirements-dev.txt

dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

test:
	docker exec engineering-test-backend_api_1 black . \
	&& docker exec engineering-test-backend_api_1 mypy . \
	&& docker exec engineering-test-backend_api_1 pytest .

stop:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

up:
	make venv && docker-compose up --build -d

down:
	docker-compose down
