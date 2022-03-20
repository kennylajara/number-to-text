env:
	python3 -m venv venv && python3 -m pip install -r requirements.txt

dev:
	make env && python3 -m pip install -r requirements-dev.txt && docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

stop:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

up:
	make env && docker-compose up --build -d

down:
	docker-compose down
