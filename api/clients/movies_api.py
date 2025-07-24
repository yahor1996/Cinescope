from Cinescope.custom_requester.custom_requester import CustomRequester
from Cinescope.constants.constants import MOVIES_ENDPOINT

class MoviesAPI(CustomRequester):
    """
    Класс для работы с API Movies.
    """

    def __init__(self, session):
        super().__init__(session=session, base_url="https://api.dev-cinescope.coconutqa.ru/")


    def create_movie(self, test_movie, expected_status=[200, 201]):
        """
        Создание нового фильма.
        :param test_movie: Данные фильма.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="POST",
            endpoint=MOVIES_ENDPOINT,
            data=test_movie,
            expected_status=expected_status
        )


    def get_movie(self, movie_id, expected_status=[200, 201]):
        """
        Получение фильма по его id.
        :param movie_id: Id фильма.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="GET",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
            data=None,
            expected_status=expected_status
        )


    def get_movies(self, params_movies, expected_status=[200, 201]):
        """
        Получение афиш фильмов.
        :param params_movies: Параметры для получения афиш фильмов.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="GET",
            endpoint=f"{MOVIES_ENDPOINT}{params_movies}",
            data=None,
            expected_status=expected_status
        )


    def delete_movie(self, movie_id, expected_status=[200, 201]):
        """
        Удаление фильма по его id.
        :param movie_id: Id фильма, который будем удалять
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="DELETE",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
            data=None,
            expected_status=expected_status
        )


    def edit_movie(self, movie_id, edited_movie, expected_status=[200, 201]):
        """
        Редактирование фильма по его id.
        :param edited_movie: Редактируемые данные фильма.
        :param movie_id: Id фильма, который будем редактировать.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="PATCH",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
            data=edited_movie,
            expected_status=expected_status
        )


    def create_review(self, movie_id, test_review, expected_status=[200, 201]):
        """
        Создание отзыва к фильму.
        :param movie_id: Id фильма.
        :param test_review: Данные отзыва.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="POST",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}/reviews",
            data=test_review,
            expected_status=expected_status
        )


    def get_reviews(self, movie_id, expected_status=[200, 201]):
        """
        Получение отзывов фильма.
        :param movie_id: Id фильма.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="GET",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}/reviews",
            data=None,
            expected_status=expected_status
        )


    def edit_review(self, movie_id, edited_review, expected_status=[200, 201]):
        """
        Редактирование отзыва фильма.
        :param movie_id: Id фильма.
        :param edited_review: Отредактированный отзыв в запросе.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="PUT",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}/reviews",
            data=edited_review,
            expected_status=expected_status
        )


    def delete_movie_review(self, params_review, expected_status=[200, 201]):
        """
        Удаление отзыва фильма.
        :param params_review: Параметры в запросе на удаление(movieId, userId)
        :param expected_status: Ожидаемый статус-код.
        """
        movie_id = params_review["movieId"]

        return self.send_request(
            method="DELETE",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}/reviews",
            data=params_review,
            expected_status=expected_status
        )


    def hide_review(self, params_review, expected_status=[200, 201]):
        """
        Скрытие отзыва фильма
        :param params_review: Параметры в запросе на скрытие отзыва(movieId, userId)
        :param expected_status: Ожидаемый статус-код.
        """
        movie_id = params_review["movieId"]
        user_id = params_review["userId"]

        return self.send_request(
            method="PATCH",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}/reviews/hide/{user_id}",
            data=params_review,
            expected_status=expected_status
        )


    def show_review(self, params_review, expected_status=[200, 201]):
        """
        Показ отзыва фильма
        :param params_review: Параметры в запросе на показ отзыва(movieId, userId)
        :param expected_status: Ожидаемый статус-код.
        """
        movie_id = params_review["movieId"]
        user_id = params_review["userId"]

        return self.send_request(
            method="PATCH",
            endpoint=f"{MOVIES_ENDPOINT}/{movie_id}/reviews/show/{user_id}",
            data=params_review,
            expected_status=expected_status
        )