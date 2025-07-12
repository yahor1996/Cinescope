from Cinescope.constants import REGISTER_ENDPOINT, LOGIN_ENDPOINT
from Cinescope.custom_requester.custom_requester import CustomRequester

class AuthAPI(CustomRequester):
    """
    Класс для работы с аутентификацией.
    """

    def __init__(self, session):
        super().__init__(session=session, base_url="https://auth.dev-cinescope.coconutqa.ru/")


    def register_user(self, user_data, expected_status=201):
        """
        Регистрация нового пользователя.
        :param user_data: Данные пользователя.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=user_data,
            expected_status=expected_status
        )


    def login_user(self, login_data, expected_status=200):
        """
        Авторизация пользователя.
        :param login_data: Данные для логина.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status=expected_status
        )


    def authenticate(self, user_creds):
        login_data = {
            "email": user_creds[0],
            "password": user_creds[1]
        }

        response = self.login_user(login_data).json()
        if "accessToken" not in response:
            raise KeyError("token is missing")

        token = response["accessToken"]
        self._update_session_headers(**{"authorization": "Bearer " + token})
        #self._update_session_headers(session=self.session, **{"authorization": "Bearer " + token})
        #return {"Authorization": f"Bearer {token}"}








# До темы апи классы
"""
import pytest
from constants import REGISTER_ENDPOINT, LOGIN_ENDPOINT

import Cinescope.constants


class TestAuthAPI:
    def test_register_user(self, requester, test_user):

        Тест на регистрацию пользователя.

        response = requester.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=test_user,
            expected_status=201
        )
        response_data = response.json()
        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    def test_register_and_login_user(self, requester, registered_user):

        Тест на регистрацию и авторизацию пользователя.

        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        response = requester.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,
            data=login_data,
            expected_status = 200
        )
        response_data = response.json()
        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
        assert response_data["user"]["email"] == registered_user["email"], "Email не совпадает"

"""











# Собственный код
"""
import pytest
import requests
from Cinescope.constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT


class TestAuthAPI:
    test_user_email = None
    test_user_password = None

    def test_register_user(self, test_user):
        # URL для регистрации
        register_url = f"{BASE_URL}{REGISTER_ENDPOINT}"

        # Отправка запроса на регистрацию
        response = requests.post(register_url, json=test_user, headers=HEADERS)

        # Логируем ответ для диагностики
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        # Проверки
        assert response.status_code == 201, "Ошибка регистрации пользователя"
        response_data = response.json()
        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"

        # Проверяем, что роль USER назначена по умолчанию
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

        TestAuthAPI.test_user_email = test_user["email"]
        TestAuthAPI.test_user_password = test_user["password"]

    def test_login_user(self):
        # URL для логина
        login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"

        # Данные для логина
        login_data = {
            "email": TestAuthAPI.test_user_email,
            "password": TestAuthAPI.test_user_password
        }

        # Отправка запроса на логин
        response = requests.post(login_url, json=login_data, headers=HEADERS)

        # Логируем ответ для диагностики
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        # Проверки
        assert response.status_code in [200, 201], "Ошибка логина пользователя"
        response_data = response.json()
        assert "accessToken" in response_data, "accessToken пользователя отсутствует в ответе"
        assert response_data["user"]["email"] == login_data["email"], "email не с корректными данными"

    def test_negative_password(self):
        invalid_password = "Qatester-1996"

        # URL для логина
        login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"

        # Данные для логина
        login_data = {
            "email": TestAuthAPI.test_user_email,
            "password": login_url
        }

        # Отправка запроса на логин c невалидным паролем
        response = requests.post(login_url, json=login_data, headers=HEADERS)

        # Логируем ответ для диагностики
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        assert response.status_code in [401, 500], "Авторизация успешна с невалидным паролем"
        response_data = response.json()
        assert "message" in response_data, "Сообщение об ошибке отсутствует в ответе"

    def test_negative_email(self):
        invalid_email = "Qatester123@mail.ru"

        # URL для логина
        login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"

        # Данные для логина
        login_data = {
            "email": invalid_email,
            "password": TestAuthAPI.test_user_password
        }

        # Отправка запроса на логин c невалидной почтой
        response = requests.post(login_url, json=login_data, headers=HEADERS)

        # Логируем ответ для диагностики
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        assert response.status_code in [401, 500], "Авторизация успешна с невалидной почтой"
        response_data = response.json()
        assert "message" in response_data, "Сообщение об ошибке отсутствует в ответе"

    def test_negative_empty_data(self):

        # URL для логина
        login_url = f"{BASE_URL}{LOGIN_ENDPOINT}"

        # Данные для логина
        login_data = {
            "email": "",
            "password": ""
        }

        # Отправка запроса на логин c невалидной почтой
        response = requests.post(login_url, json=login_data, headers=HEADERS)

        # Логируем ответ для диагностики
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        assert response.status_code in [401, 500], "Авторизация успешна c пустым телом в запросе"
        response_data = response.json()
        assert "message" in response_data, "Сообщение об ошибке отсутствует в ответе"
"""
