from playwright.sync_api import Page, expect
import random
import string
from faker import Faker
import time

faker = Faker()

def test_registration(page: Page):
    page.goto('https://dev-cinescope.coconutqa.ru/register')

    username_locator = 'input[name="fullName"]'
    email_locator = 'input[name="email"]'
    password_locator = 'input[name="password"]'
    repeat_password_locator = 'input[name="passwordRepeat"]'
    register_button_locator = '//button[text()="Зарегистрироваться"]'

    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    user_email = f"tst{random_string}@gmail.com"

    page.fill(username_locator, 'Жмышенко Валерий Альбертович')
    page.fill(email_locator, user_email)
    page.fill(password_locator, 'qwerty123Q')
    page.fill(repeat_password_locator, 'qwerty123Q')
    page.locator(register_button_locator).click()

    page.wait_for_url('https://dev-cinescope.coconutqa.ru/login')
    expect(page.get_by_text("Подтвердите свою почту")).to_be_visible(visible=True)

    time.sleep(10)
