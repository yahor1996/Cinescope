from sqlalchemy.orm import sessionmaker, Session

from Cinescope.conftest.conftest import *
from Cinescope.db_requester.models import UserDBModel
from Cinescope.resources.user_creds import SuperAdminCreds
from Cinescope.models.base_models import RegisterUserResponse
from Cinescope.models.registration_and_login_model import RegisterAndLoginUserResponse

class TestAuthAPI:
    """
        def test_register_user(self, api_manager: ApiManager, test_user):

        Тест на регистрацию пользователя.

        response = api_manager.auth_api.register_user(test_user)
        response_data = response.json()

        # Проверки
        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"
    """



    def test_register_user(self, api_manager: ApiManager, test_user):
        response = api_manager.auth_api.register_user(user_data=test_user)
        register_user_response = RegisterUserResponse(**response.json())
        assert register_user_response.email == test_user.email, "Email не совпадает"


    def test_register_and_login_user(self, api_manager: ApiManager, registered_user):
        """
        Тест на регистрацию и авторизацию пользователя.
        """
        login_data = {
            "email": registered_user.email,
            "password": registered_user.password
        }
        response = api_manager.auth_api.login_user(login_data)
        response_data = RegisterAndLoginUserResponse(**response.json())

        assert response_data.user.email == registered_user.email, "Email не совпадает"


    @pytest.mark.parametrize("email, password, expected_status", [
        (f"{SuperAdminCreds.USERNAME}", f"{SuperAdminCreds.PASSWORD}", [200, 201]),
        ("test_login1@email.com", "asdqwe123Q!", [401]),  # Сервис не может обработать логин по незареганному юзеру
        ("", "password", [401]),
    ], ids=["Admin login", "Invalid user", "Empty username"])
    def test_login(self, email, password, expected_status, api_manager):
        login_data = {
            "email": email,
            "password": password
        }
        api_manager.auth_api.login_user(login_data=login_data, expected_status=expected_status)


    def test_register_user_db_session(self, api_manager: ApiManager, test_user: TestUser, db_session: Session):
        """
        Тест на регистрацию пользователя с проверкой в базе данных.
        """
        # выполняем запрос на регистрацию нового пользователя
        response = api_manager.auth_api.register_user(test_user)
        register_user_response = RegisterUserResponse(**response.json())

        # Проверяем добавил ли сервис Auth нового пользователя в базу данных
        users_from_db = db_session.query(UserDBModel).filter(UserDBModel.id == register_user_response.id)

        # Получили объект из базы данных и проверили что он действительно существует в единственном экземпляре
        assert users_from_db.count() == 1, "объект не попал в базу данных"
        # Достаем первый и единственный объект из списка полученных
        user_from_db = users_from_db.first()
        # Можем осуществить проверку всех полей в базе данных например Email
        assert user_from_db.email == test_user.email, "Email не совпадает"