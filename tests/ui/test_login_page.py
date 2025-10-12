import allure
import time
import pytest
from playwright.sync_api import sync_playwright
from Cinescope.models.page_object_models import CinescopLoginPage
from Cinescope.conftest.conftest import *


@allure.epic("Тестирование UI")
@allure.feature("Тестирование Страницы Login")
@pytest.mark.ui
class TestloginPage:
    @allure.title("Проведение успешного входа в систему")
    def test_login_by_ui(self, registered_user):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)  # Запуск браузера headless=False для визуального отображения
            page = browser.new_page()
            login_page = CinescopLoginPage(page)  # Создаем объект страницы Login

            login_page.open()
            login_page.login(registered_user.email, registered_user.password)  # Осуществяем вход
            time.sleep(5)

            login_page.reload() # Фронтовый баг при логине, делаем обновление страницы

            login_page.assert_was_redirect_to_home_page()  # Проверка редиректа на домашнюю страницу
            login_page.make_screenshot_and_attach_to_allure()  # Прикрепляем скриншот
            #login_page.assert_allert_was_pop_up()  # Проверка появления и исчезновения алерта

            # Пауза для визуальной проверки (нужно удалить в реальном тестировании)
            time.sleep(5)
            browser.close()





"""
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
"""