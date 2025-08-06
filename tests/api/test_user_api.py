from Cinescope.conftest.conftest import creation_user_data
from Cinescope.conftest.conftest import *
from Cinescope.models.base_models import RegisterUserResponse


class TestUser:

    def test_create_user(self, super_admin, creation_user_data):
        """
        Создание пользователя с правами супер админа
        """
        response = super_admin.api.user_api.create_user(creation_user_data)
        created_user_response = RegisterUserResponse(**response.json())

        assert created_user_response.id != '', "ID должен быть не пустым"
        assert created_user_response.email == creation_user_data.email
        assert created_user_response.fullName == creation_user_data.fullName
        assert created_user_response.roles == creation_user_data.roles
        assert created_user_response.verified is True


    def test_get_user_by_locator(self, super_admin, creation_user_data):
        response = super_admin.api.user_api.create_user(creation_user_data)
        created_user_response = RegisterUserResponse(**response.json())

        response_by_id = super_admin.api.user_api.get_user(created_user_response.id)
        get_response_by_id = RegisterUserResponse(**response_by_id.json())

        response_by_email = super_admin.api.user_api.get_user(creation_user_data.email)
        get_response_by_email = RegisterUserResponse(**response_by_email.json())

        assert get_response_by_id == get_response_by_email, "Содержание ответов должно быть идентичным"
        assert get_response_by_id.id != '', "ID должен быть не пустым"
        assert get_response_by_id.email == creation_user_data.email
        assert get_response_by_id.fullName == creation_user_data.fullName
        assert get_response_by_id.roles == creation_user_data.roles
        assert get_response_by_id.verified is True


    def test_get_user_by_id_common_user(self, common_user):
        common_user.api.user_api.get_user(common_user.email, expected_status=[403])

