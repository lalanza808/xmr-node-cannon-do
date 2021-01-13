setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

dev-up:
	docker-compose up -d
	./bin/dev_wallets

prod-up:
	docker-compose up -d
	./bin/prod_wallets

down:
	docker-compose down
	./bin/stop_wallets

dev:
	./bin/dev_app

prod:
	./bin/prod_app

init:
	./bin/cmd init

dbshell:
	docker-compose exec db psql -U nodecannon
