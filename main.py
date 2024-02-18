from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

from src.booking import Booking
from src.config import BookingConfig

if __name__ == '__main__':
    booking_config = BookingConfig()
    driver_options = Options()
    if booking_config.headless():
        driver_options.add_argument('--headless')
    browser = Firefox(driver_options)
    booking = Booking(browser, booking_config)
    booking.start()
