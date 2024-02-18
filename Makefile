start-webdriver:
	sudo docker-compose -f docker-compose-driver.yml up -d

start-booking:
	sudo docker-compose -f docker-compose.yml up

stop-webdriver:
	sudo docker-compose -f docker-compose-driver.yml down

stop-booking:
	sudo docker-compose -f docker-compose.yml down