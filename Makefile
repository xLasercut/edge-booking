start-webdriver:
	sudo docker compose -f docker-compose-driver.yml up -d

start-booking: build-booking
	sudo docker compose -f docker-compose.yml up

stop-webdriver:
	sudo docker compose -f docker-compose-driver.yml down

stop-booking:
	sudo docker compose -f docker-compose.yml down

build-booking:
	sudo docker compose -f docker-compose.yml build