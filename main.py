from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from datetime import datetime

USERNAME = ''
PASSWORD = ''


def click_cookie_button(browser: Firefox):
    cookie_button = browser.find_element(By.TAG_NAME, 'button')
    while cookie_button.text != 'Accept':
        cookie_button = browser.find_element(By.TAG_NAME, 'button')
    cookie_button.click()


def login(browser: Firefox):
    username_input = browser.find_element(By.ID, 'xn-Username')
    password_input = browser.find_element(By.ID, 'xn-Password')
    login_button = browser.find_element(By.ID, 'login')
    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)
    login_button.click()


def go_to_online_booking(browser: Firefox):
    browser.find_element(By.ID, 'xn-online-booking-link').click()
    browser.implicitly_wait(5)
    browser.find_element(By.XPATH, '//span[text()="What do you want to do?"]').click()
    browser.find_element(By.ID, 'toggleActivitiesOn').click()
    browser.find_element(By.ID, 'toggleClassesOff').click()
    browser.find_element(By.XPATH, '//div[text()="Badminton"]').click()


def main():
    browser = Firefox()
    browser.get('https://sportsbookings.leeds.ac.uk/lhweb/identity/login')
    click_cookie_button(browser)
    login(browser)
    go_to_online_booking(browser)

    browser.quit()


if __name__ == '__main__':
    main()
