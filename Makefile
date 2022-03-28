dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

test:
	docker exec zesty-test_api_1 black . \
	&& docker exec zesty-test_api_1 mypy . \
	&& docker exec zesty-test_api_1 pytest .

stop:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

up:
	docker-compose up --build -d

down:
	docker-compose down
