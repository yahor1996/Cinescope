from Cinescope.conftest.conftest import common_user, params_movies, api_manager, super_admin
from Cinescope.conftest.conftest import *
from urllib.parse import urlencode


class TestMoviesAPI:
    def test_create_movie(self, super_admin, test_movie):
        """
        Тест на создание фильма
        """
        response = super_admin.api.movies_api.create_movie(test_movie)
        response_data = response.json()

        # Проверки
        assert response_data["name"] == test_movie["name"], "Название фильма не совпадает"
        assert response_data["description"] == test_movie["description"], "Описание фильма не совпадает"


    @pytest.mark.slow
    def test_get_movie(self, super_admin, created_movie):
        """
        Тест на получение фильма по id
        """
        movie_id = created_movie["id"]
        response = super_admin.api.movies_api.get_movie(movie_id)
        response_data = response.json()

        # Проверки
        assert "id" in response_data, "ID фильма отсутствует в ответе"
        assert "name" in response_data, "Имя фильма отсутствует в ответе"
        assert "description" in response_data, "Описание фильма отсутствует в ответе"


    def test_get_movies(self, common_user, params_movies):
        """
        Тест на получение афиш фильмов
        """
        response = common_user.api.movies_api.get_movies(params_movies)
        response_data = response.json()

        # Проверки
        assert "movies" in response_data, "Список фильмов отсутствует в ответе"
        assert "page" in response_data, "Атрибут страницы отсутствует в ответе"


    @pytest.mark.slow
    def test_get_movies_filter(self, get_movies_created_date):
        """
        Тест на проверку работы фильтров
        """
        assert get_movies_created_date == sorted(get_movies_created_date), "Даты не отфильтрованы asc"


    @pytest.mark.parametrize("price,locations,genre_id", [(range(1, 1001), "SPB", 1)])
    def test_get_movies_params(self, price, locations, genre_id, api_manager):
        """
        Тест на проверку параметризованных фильтров
        """

        # Определение параметров в виде словаря
        params = {
            'minPrice': min(price),
            'maxPrice': max(price),
            'locations': locations,
            'genreId': genre_id
        }

        # Формирование строки запроса
        params_movies = f'?{urlencode(params)}'
        api_manager.movies_api.get_movies(params_movies)


    @pytest.mark.slow
    def test_delete_movie(self, super_admin, common_user, delete_created_movie):
        """
        Тест на удаление фильма по id
        """
        movie_id = delete_created_movie["id"]
        response = super_admin.api.movies_api.delete_movie(movie_id)
        response_data = response.json()

        # Проверки
        assert "id" in response_data, "ID фильма отсутствует в ответе"
        assert "name" in response_data, "Имя фильма отсутствует в ответе"
        assert "description" in response_data, "Описание фильма отсутствует в ответе"

        # Проверка, что фильм действительно удалился
        response = common_user.api.movies_api.get_movie(movie_id, expected_status=[404])
        response_data = response.json()

        assert "message" in response_data, "Отсутствует сообщение в ответе"


    @pytest.mark.parametrize("user_factory,expected_status", [
        ("super_admin", [200, 201]),
        ("common_user", [403]),
        ("admin_user", [403])
    ])
    def test_delete_movie_params(self, user_factory, expected_status, delete_created_movie, request):
        """
        Тест на проверку удаления фильма под разными ролями
        """
        user = request.getfixturevalue(user_factory)
        movie_id = delete_created_movie["id"]
        user.api.movies_api.delete_movie(movie_id, expected_status=expected_status)


    def test_edit_movie(self, super_admin, created_movie, edited_movie):
        """
        Тест на редактирование фильма
        """
        movie_id = created_movie["id"]
        response = super_admin.api.movies_api.edit_movie(movie_id, edited_movie)
        response_data = response.json()

        # Проверки
        assert response_data["name"] != created_movie["name"], "Название фильма не изменилось"
        assert response_data["location"] == created_movie["location"], "Локация изменилась"


class TestReviewsAPI:
    def test_create_review(self, common_user, test_review, created_movie):
        """
        Тест на создание отзыва к фильму
        """
        movie_id = created_movie["id"]
        response = common_user.api.movies_api.create_review(movie_id, test_review)
        response_data = response.json()

        # Проверки
        assert "rating" in response_data, "Рейтинг фильма отсутствует в ответе"
        assert "text" in response_data, "Отзыв о фильме отсутствует в ответе"


    @pytest.mark.slow
    def test_get_reviews(self, common_user, created_movie, created_review):
        """
        Тест на получение отзывов фильма
        """
        movie_id = created_movie["id"]
        response = common_user.api.movies_api.get_reviews(movie_id)
        response_data = response.json()

        # Проверяем наличие ключа rating хотя бы в одном из словарей списка response_data
        assert any("rating" in element for element in response_data), "Рейтинг фильма отсутствует в ответе"
        assert any("text" in element for element in response_data), "Отзыв о фильме отсутствует в ответе"


    def test_edit_review(self, super_admin, created_movie, edited_review, test_review):
        """
        Тест на редактирование отзыва фильма
        """
        movie_id = created_movie["id"]
        response = super_admin.api.movies_api.edit_review(movie_id, edited_review)
        response_data = response.json()

        # Проверки
        assert response_data["text"] != test_review["text"], "Текст отзыва не изменился"


    def test_delete_reviews(self, super_admin, common_user, created_movie, delete_created_review):
        """
        Тест на удаление отзыва к фильму
        """
        params_review = {
            "movieId": created_movie["id"],
            "userId": delete_created_review["userId"]
        }

        super_admin.api.movies_api.delete_movie_review(params_review)

        # Проверка, что отзыв действительно удалился
        response = common_user.api.movies_api.get_reviews(params_review["movieId"])
        response_data = response.json()
        assert response_data == [], "Отзыв не удалён"


    def test_hide_review(self, super_admin, created_movie, created_review):
        """
        Тест на скрытие отзыва
        """
        params_review = {
            "movieId": created_movie["id"],
            "userId": created_review["userId"]
        }

        response = super_admin.api.movies_api.hide_review(params_review)
        response_data = response.json()

        # Проверки
        assert "text" in response_data, "Отзыв к фильму отсутствует"


    @pytest.mark.slow
    def test_show_review(self, super_admin, created_movie, hidden_review):
        """
        Тест на показ отзыва
        """
        params_review = {
            "movieId": created_movie["id"],
            "userId": hidden_review["userId"]
        }

        response = super_admin.api.movies_api.show_review(params_review)
        response_data = response.json()

        # Проверки
        assert "text" in response_data, "Отзыв к фильму отсутствует"


class TestNegativeMoviesAPI:
    def test_negative_create_movie(self, super_admin, test_movie):
        """
        Негативный тест на создание фильма
        """
        test_movie["name"] = None
        response = super_admin.api.movies_api.create_movie(test_movie, expected_status=[400])
        response_data = response.json()

        # Проверки
        assert "error" in response_data, "Отсутствие error Bad Request в ответе"
        assert "message" in response_data, "Сообщение об ошибке отсутствует в ответе"


    def test_negative_roles_create_movie(self, common_user, test_movie):
        """
        Негативный тест на создание фильма с ролью USER
        """
        response = common_user.api.movies_api.create_movie(test_movie, expected_status=[403])
        response_data = response.json()

        # Проверки
        assert "error" in response_data, "Отсутствие error Forbidden в ответе"
        assert "message" in response_data, "Сообщение об ошибке 'Forbidden resource' отсутствует в ответе"


    def test_negative_get_movie(self, common_user, created_movie):
        """
        Негативный тест на получение фильма по id
        """
        movie_id = None
        response = common_user.api.movies_api.get_movie(movie_id, expected_status=[500])
        response_data = response.json()

        # Проверки
        assert "statusCode" in response_data, "Отсутствие ошибки со statusCode 500"
        assert "message" in response_data, "Сообщение об ошибке отсутствует в ответе"


    def test_negative_get_movies(self, common_user, params_movies):
        """
        Негативный тест на получение афиш фильмов
        """
        params_movies = "test"

        response = common_user.api.movies_api.get_movies(params_movies, expected_status=[404])
        response_data = response.json()

        # Проверки
        assert "error" in response_data, "Отсутствие error Not Found в ответе"
        assert "message" in response_data, "Сообщение об ошибке отсутствует в ответе"


    def test_negative_delete_movie(self, super_admin, created_movie):
        """
        Негативный тест на удаление фильма по id
        """
        movie_id = None
        response = super_admin.api.movies_api.delete_movie(movie_id, expected_status=[404])
        response_data = response.json()

        # Проверки
        assert "error" in response_data, "Отсутствие error Not Found в ответе"
        assert "message" in response_data, "Сообщение об ошибке отсутствует в ответе"


    def test_negative_edit_movie(self, super_admin, created_movie, edited_movie):
        """
        Негативный тест на редактирование фильма
        """
        edited_movie["name"] = None
        movie_id = created_movie["id"]
        response = super_admin.api.movies_api.edit_movie(movie_id, edited_movie, expected_status=[404])
        response_data = response.json()

        # Проверки
        assert "error" in response_data, "Отсутствие error Not Found в ответе"
        assert "message" in response_data, "Сообщение об ошибке отсутствует в ответе"
