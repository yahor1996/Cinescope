from Cinescope.tests.api.api_manager import ApiManager


class TestMoviesAPI:
    def test_create_movie(self, api_manager: ApiManager, test_movie):
        """
        Тест на создание фильма
        """
        response = api_manager.movies_api.create_movie(test_movie)
        response_data = response.json()

        # Проверки
        assert response.status_code == 201, "Фильм не создался"
        assert response_data["name"] == test_movie["name"], "Название фильма не совпадает"
        assert response_data["description"] == test_movie["description"], "Описание фильма не совпадает"


    def test_get_movie(self, api_manager: ApiManager, created_movie):
        """
        Тест на получение фильма по id
        """
        movie_id = created_movie["id"]
        response = api_manager.movies_api.get_movie(movie_id)
        response_data = response.json()

        # Проверки
        assert response.status_code == 200, "Фильм по id не найден"
        assert "id" in response_data, "ID фильма отсутствует в ответе"
        assert "name" in response_data, "Имя фильма отсутствует в ответе"
        assert "description" in response_data, "Описание фильма отсутствует в ответе"


    def test_get_movies(self, api_manager: ApiManager, parameters_movies):
        """
        Тест на получение афиш фильмов
        """
        response = api_manager.movies_api.get_movies(parameters_movies)
        response_data = response.json()

        # Проверки
        assert response.status_code == 200, "Афишы фильмов не найдены"
        assert "movies" in response_data, "Список фильмов отсутствует в ответе"
        assert "page" in response_data, "Атрибут страницы отсутствует в ответе"


    def test_get_movies_filter(self, get_movies_created_date):
        """
        Тест на проверку работы фильтров
        """
        assert get_movies_created_date == sorted(get_movies_created_date), "Даты не отфильтрованы asc"


    def test_delete_movie(self, api_manager: ApiManager, created_movie):
        """
        Тест на удаление фильма по id
        """
        movie_id = created_movie["id"]
        response = api_manager.movies_api.delete_movie(movie_id)
        response_data = response.json()

        # Проверки
        assert response.status_code == 200, "Фильм не удалился"
        assert "id" in response_data, "ID фильма отсутствует в ответе"
        assert "name" in response_data, "Имя фильма отсутствует в ответе"
        assert "description" in response_data, "Описание фильма отсутствует в ответе"

        # Проверка, что фильм действительно удалился
        response = api_manager.movies_api.get_movie(movie_id, expected_status=404)
        response_data = response.json()

        assert "message" in response_data, "Отсутствует сообщение в ответе"


    def test_edit_movie(self, api_manager: ApiManager, created_movie, edited_movie):
        """
        Тест на редактирование фильма
        """
        movie_id = created_movie["id"]
        response = api_manager.movies_api.edit_movie(movie_id, edited_movie)
        response_data = response.json()

        # Проверки
        assert response.status_code == 200, "Данные фильма не обновились"
        assert response_data["name"] != created_movie["name"], "Название фильма не изменилось"
        assert response_data["location"] == created_movie["location"], "Локация изменилась"


class TestReviewsAPI:
    def test_create_review(self, api_manager: ApiManager, test_review, created_movie):
        """
        Тест на создание отзыва к фильму
        """

        movie_id = created_movie["id"]
        response = api_manager.movies_api.create_review(movie_id, test_review)
        response_data = response.json()

        # Проверки
        assert response.status_code == 201, "Отзыв не создался"
        assert "rating" in response_data, "Рейтинг фильма отсутствует в ответе"
        assert "text" in response_data, "Отзыв о фильме отсутствует в ответе"


    def test_get_reviews(self, api_manager: ApiManager, created_movie, created_review):
        """
        Тест на получение отзывов фильма
        """
        movie_id = created_movie["id"]
        response = api_manager.movies_api.get_reviews(movie_id)
        response_data = response.json()

        # Проверки
        assert response.status_code == 200, "Отзыв не получен в ответе"

        # Проверяем наличие ключа rating хотя бы в одном из словарей списка response_data
        assert any("rating" in element for element in response_data), "Рейтинг фильма отсутствует в ответе"
        assert any("text" in element for element in response_data), "Отзыв о фильме отсутствует в ответе"


    def test_edit_review(self, api_manager: ApiManager, created_movie, edited_review, test_review):
        """
        Тест на редактирование отзыва фильма
        """
        movie_id = created_movie["id"]
        response = api_manager.movies_api.edit_review(movie_id, edited_review)
        response_data = response.json()

        # Проверки
        assert response.status_code == 200, "Отзыв не отредактирован"
        assert response_data["text"] != test_review["text"], "Текст отзыва не изменился"


    def test_delete_reviews(self, api_manager: ApiManager, created_movie, created_review):
        """
        Тест на удаление отзыва к фильму
        """
        parameters_review = {
            "movieId": created_movie["id"],
            "userId": created_review["userId"]
        }

        response = api_manager.movies_api.delete_movie_review(parameters_review)
        response_data = response.json()

        # Проверки
        assert response.status_code == 200, "Отзыв не удалён"

        # Проверка, что отзыв действительно удалился
        response = api_manager.movies_api.get_reviews(parameters_review["movieId"])
        response_data = response.json()
        assert response_data == [], "Отзыв не удалён"


    def test_hide_review(self, api_manager: ApiManager, created_movie, created_review):
        """
        Тест на скрытие отзыва
        """
        parameters_review = {
            "movieId": created_movie["id"],
            "userId": created_review["userId"]
        }

        response = api_manager.movies_api.hide_review(parameters_review)
        response_data = response.json()

        # Проверки
        assert response.status_code == 200, "Отзыв не скрыт"
        assert response_data["hidden"] == True, "Признак скрытия - False"


    def test_show_review(self, api_manager: ApiManager, created_movie, hidden_review):
        """
        Тест на показ отзыва
        """
        parameters_review = {
            "movieId": created_movie["id"],
            "userId": hidden_review["userId"]
        }


        response = api_manager.movies_api.show_review(parameters_review)
        response_data = response.json()

        # Проверки
        assert response.status_code == 200, "Отзыв скрыт"
        assert response_data["hidden"] == False, "Признак скрытия - True"


class TestNegativeMoviesAPI:
    def test_negative_create_movie(self, api_manager: ApiManager, test_movie):
        """
        Негативный тест на создание фильма
        """
        test_movie["name"] = None
        response = api_manager.movies_api.create_movie(test_movie, expected_status=400)
        response_data = response.json()

        # Проверки
        assert response.status_code == 400, "Фильм создался c name = None"
        assert "error" in response_data, "Отсутствие error Bad Request в ответе"
        assert "message" in response_data, "Сообщение об ошибке отсутствует в ответе"


    def test_negative_get_movie(self, api_manager: ApiManager, created_movie):
        """
        Негативный тест на получение фильма по id
        """
        movie_id = None
        response = api_manager.movies_api.get_movie(movie_id, expected_status=500)
        response_data = response.json()

        # Проверки
        assert response.status_code == 500, "Фильм по id = None найден"
        assert "error" in response_data, "Отсутствие error Internal Server Error в ответе"
        assert "message" in response_data, "Сообщение об ошибке отсутствует в ответе"


    def test_negative_get_movies(self, api_manager: ApiManager, parameters_movies):
        """
        Негативный тест на получение афиш фильмов
        """
        parameters_movies = str(parameters_movies)

        response = api_manager.movies_api.get_movies(parameters_movies, expected_status=400)
        response_data = response.json()

        # Проверки
        assert response.status_code == 400, "Афишы фильмов отображаются"
        assert "error" in response_data, "Отсутствие error Bad Request в ответе"
        assert "message" in response_data, "Сообщение об ошибке отсутствует в ответе"


    def test_negative_delete_movie(self, api_manager: ApiManager, created_movie):
        """
        Негативный тест на удаление фильма по id
        """
        movie_id = None
        response = api_manager.movies_api.delete_movie(movie_id, expected_status=404)
        response_data = response.json()

        # Проверки
        assert response.status_code == 404, "Фильм c movie_id = None удалился"
        assert "error" in response_data, "Отсутствие error Not Found в ответе"
        assert "message" in response_data, "Сообщение об ошибке отсутствует в ответе"


    def test_negative_edit_movie(self, api_manager: ApiManager, created_movie, edited_movie):
        """
        Негативный тест на редактирование фильма
        """
        edited_movie["name"] = None
        movie_id = created_movie["id"]
        response = api_manager.movies_api.edit_movie(movie_id, edited_movie, expected_status=400)
        response_data = response.json()

        # Проверки
        assert response.status_code == 400, "Данные фильма обновились"
        assert "error" in response_data, "Отсутствие error Bad Request в ответе"
        assert "message" in response_data, "Сообщение об ошибке отсутствует в ответе"
