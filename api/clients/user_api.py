from Cinescope.custom_requester.custom_requester import CustomRequester


class UserAPI(CustomRequester):

    USER_BASE_URL = "https://auth.dev-cinescope.coconutqa.ru/"

    def __init__(self, session):
        self.session = session
        super().__init__(session, self.USER_BASE_URL)


    def get_user(self, user_locator, expected_status=200):
        return self.send_request(
            method="GET",
            endpoint=f"user/{user_locator}",
            expected_status=expected_status
        )

    def create_user(self, user_data, expected_status=201):
        return self.send_request(
            method="POST",
            endpoint="user",
            data=user_data,
            expected_status=expected_status
        )

    def update_user(self, user_locator, user_data, expected_status=200):
        return self.send_request(
            method="PATCH",
            endpoint=f"user/{user_locator}",
            data=user_data,
            expected_status=expected_status
        )


"""
from Cinescope.custom_requester.custom_requester import CustomRequester

class UserAPI(CustomRequester):

    Класс для работы с API пользователей.

    def __init__(self, session):
        super().__init__(session=session, base_url="https://auth.dev-cinescope.coconutqa.ru/")

    def get_user_info(self, user_id, expected_status=200):

        Получение информации о пользователе.
        :param user_id: ID пользователя.
        :param expected_status: Ожидаемый статус-код.

        return self.send_request(
            method="GET",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )

    def delete_user(self, user_id, expected_status=204):

        Удаление пользователя.
        :param user_id: ID пользователя.
        :param expected_status: Ожидаемый статус-код.

        return self.send_request(
            method="DELETE",
            endpoint=f"/user/{user_id}",
            expected_status=expected_status
        )
"""
