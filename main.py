import time

import schedule
from selenium.webdriver import Remote
from selenium.webdriver.firefox.options import Options

from src.booking import Booking
from src.config import BookingConfig


def booking_job():
    booking_config = BookingConfig()
    driver_options = Options()
    if booking_config.headless():
        driver_options.add_argument('--headless')
    browser = Remote(command_executor="http://localhost:4444", options=driver_options)
    booking = Booking(browser, booking_config)
    booking.start()


if __name__ == '__main__':
    print("started booking jobs")
    schedule.every().day.at("05:50").do(booking_job)
    schedule.every().day.at("06:00").do(booking_job)
    schedule.every().day.at("06:10").do(booking_job)
    while True:
        schedule.run_pending()
        time.sleep(1)
