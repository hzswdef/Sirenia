COMMAND = docker compose -f ./environments/localhost/compose.yml --env-file ./.env

up:
	$(COMMAND) up -d

start:
	$(COMMAND) start

stop:
	$(COMMAND) stop

restart:
	$(COMMAND) stop
	$(COMMAND) start

logs:
	$(COMMAND) logs -f

rm:
	$(COMMAND) stop
	$(COMMAND) rm --force