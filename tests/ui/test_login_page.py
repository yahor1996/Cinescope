import time
from playwright.sync_api import sync_playwright

from Cinescope.models.page_object_models import CinescopLoginPage
from Cinescope.conftest.conftest import *

def test_login_by_ui(registered_user):
   with sync_playwright() as playwright:
        # Запуск браузера
        browser = playwright.chromium.launch(headless=False)  # headless=False для визуального отображения
        page = browser.new_page()

        # Создаем объект страницы регистрации cinescope
        login_page = CinescopLoginPage(page)

        # Открываем страницу
        login_page.open()
        login_page.login(registered_user.email, registered_user.password)
        time.sleep(5)

        # баг на фронте с логином, рефреш костыль
        login_page.reload()

        # Проверка редиректа на домашнюю страницу
        login_page.wait_redirect_to_home_page()

        # Пауза для визуальной проверки (нужно удалить в реальном тестировании)
        time.sleep(5)

        # Закрываем браузер
        browser.close()
