from Cinescope.conftest.conftest import *
from Cinescope.resources.user_creds import SuperAdminCreds

class TestAuthAPI:
    def test_register_user(self, api_manager: ApiManager, registration_user_data):
        """
        Тест на регистрацию пользователя.
        """
        response = api_manager.auth_api.register_user(registration_user_data)
        response_data = response.json()

        # Проверки
        assert response_data["email"] == registration_user_data["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"



    def test_register_and_login_user(self, api_manager: ApiManager, registered_user):
        """
        Тест на регистрацию и авторизацию пользователя.
        """
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()

        # Проверки
        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
        assert response_data["user"]["email"] == registered_user["email"], "Email не совпадает"



    @pytest.mark.parametrize("email, password, expected_status", [
        (f"{SuperAdminCreds.USERNAME}", f"{SuperAdminCreds.PASSWORD}", 201),
        ("test_login1@email.com", "asdqwe123Q!", 401),  # Сервис не может обработать логин по незареганному юзеру
        ("", "password", 401),
    ], ids=["Admin login", "Invalid user", "Empty username"])
    def test_login(self, email, password, expected_status, api_manager):
        login_data = {
            "email": email,
            "password": password
        }
        api_manager.auth_api.login_user(login_data=login_data, expected_status=expected_status)