from faker import Faker
import pytest
import requests

from Cinescope.api.clients.api_manager import ApiManager
from Cinescope.api.clients.auth_api import AuthAPI
from Cinescope.constants.constants import BASE_URL, REGISTER_ENDPOINT, USER_CREDS, HEADERS, MOVIES_ENDPOINT
from Cinescope.constants.roles import Roles
from Cinescope.resources.user_creds import SuperAdminCreds
from Cinescope.entities.user import User
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator


faker = Faker()

@pytest.fixture(scope="function")
def test_user():
    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": [Roles.USER.value]
    }


@pytest.fixture(scope="function")
def registered_user(requester, test_user):
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    response = requester.send_request(
        method="POST",
        endpoint=REGISTER_ENDPOINT,
        data=test_user,
        expected_status=201
    )
    response_data = response.json()
    registered_user = test_user.copy()
    registered_user["id"] = response_data["id"]
    return registered_user


@pytest.fixture(scope="function")
def test_movie():
    """
    Генерация тестового фильма для тестов.
    """
    random_movie_name = DataGenerator.generate_random_movie_name()
    random_movie_price = DataGenerator.generate_random_movie_price()
    random_movie_description = DataGenerator.generate_random_movie_description()
    random_movie_genreId = DataGenerator.generate_random_movie_genreId()

    return {
        "name": random_movie_name,
        "imageUrl": "https://example.com/image.png",
        "price": random_movie_price,
        "description": random_movie_description,
        "location": "SPB",
        "published": True,
        "genreId": random_movie_genreId
    }


@pytest.fixture(scope="function")
def test_review():
    """
    Генерация тестового отзыва к фильму
    """
    random_movie_review_rating = DataGenerator.generate_random_movie_rating()
    random_movie_review_text = DataGenerator.generate_random_movie_review_text()

    return {
        "rating": random_movie_review_rating,
        "text": random_movie_review_text
    }


@pytest.fixture(scope="function")
def edited_movie(test_movie):
    """
    Отредактированный фильм для теста с обновлением (PATCH)
    """
    random_movie_name = DataGenerator.generate_random_movie_name() + "_"
    random_movie_price = DataGenerator.generate_random_movie_price()
    random_movie_description = DataGenerator.generate_random_movie_description() + "_"
    random_movie_genreId = DataGenerator.generate_random_movie_genreId()

    test_movie["name"] = random_movie_name
    test_movie["description"] = random_movie_description
    test_movie["price"] = random_movie_price
    test_movie["genreId"] = random_movie_genreId

    return test_movie


@pytest.fixture(scope="function")
def edited_review(created_review, test_review):
    """
    Отредактированный отзыв для теста редактирования отзыва (PUT)
    """
    return {
        "rating": 3,
        "text": test_review["text"] + "_"
    }


@pytest.fixture(scope="function")
def created_movie(super_admin, test_movie):
    """
    Фикстура для создания фильма и получения его данных
    """
    response = super_admin.api.movies_api.send_request(
        method="POST",
        endpoint=MOVIES_ENDPOINT,
        data=test_movie,
        expected_status=201
    )

    created_movie = response.json()
    yield created_movie

    # Очистка после теста
    movie_id = created_movie["id"]
    super_admin.api.movies_api.send_request(
        method="DELETE",
        endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
        expected_status=200
    )


@pytest.fixture(scope="function")
def delete_created_movie(super_admin, test_movie):
    """
    Фикстура для создания фильма для метода delete
    """
    response = super_admin.api.movies_api.send_request(
        method="POST",
        endpoint=MOVIES_ENDPOINT,
        data=test_movie,
        expected_status=201
    )

    new_movie = response.json()
    return new_movie


@pytest.fixture(scope="function")
def created_review(super_admin, created_movie, test_review):
    """
    Фикстура для создания отзыва к фильму
    """
    movie_id = created_movie["id"]

    response = super_admin.api.movies_api.send_request(
        method="POST",
        endpoint=f"{MOVIES_ENDPOINT}/{movie_id}/reviews",
        data=test_review,
        expected_status=201
    )

    created_review = response.json()
    yield created_review

    # Очистка после теста
    super_admin.api.movies_api.send_request(
        method="DELETE",
        endpoint=f"{MOVIES_ENDPOINT}/{movie_id}/reviews",
        data=created_review,
        expected_status=200
    )


@pytest.fixture(scope="function")
def delete_created_review(super_admin, created_movie, test_review):
    """
    Фикстура для создания отзыва к фильму для метода delete
    """
    movie_id = created_movie["id"]

    response = super_admin.api.movies_api.send_request(
        method="POST",
        endpoint=f"{MOVIES_ENDPOINT}/{movie_id}/reviews",
        data=test_review,
        expected_status=201
    )

    new_review = response.json()
    return new_review


@pytest.fixture(scope="function")
def hidden_review(api_manager, created_movie, created_review):
    """
    Фикстура для создания скрытого отзыва к фильму
    """
    params_review = {
        "movieId": created_movie["id"],
        "userId": created_review["userId"]
    }

    response = api_manager.movies_api.hide_review(params_review)
    response_data = response.json()

    return response_data


@pytest.fixture(scope="session")
def params_movies():
    """
    Фикстура с параметрами афиш фильмов.
    """
    random_page_size = DataGenerator.generate_random_page_size()
    random_page = DataGenerator.generate_random_page()
    random_min_price = DataGenerator.generate_random_min_price()
    random_max_price = DataGenerator.generate_random_max_price()

    return {
        "pageSize" : random_page_size,
        "page" : random_page,
        "minPrice" : random_min_price,
        "maxPrice" : random_max_price,
        "locations" : "MSK,SPB",
        "published" : True,
        "createdAt" : "asc"
    }


@pytest.fixture(scope="function")
def get_movies_created_date(common_user, params_movies):
    """
    Фикстура для получения даты создания фильмов.
    """
    response = common_user.api.movies_api.send_request(
        method="GET",
        endpoint=MOVIES_ENDPOINT,
        data=params_movies,
        expected_status=200
    )

    response_data = response.json()

    created_date_movies = []
    movies = response_data["movies"]
    for date_creation in movies:
        created_date_movies.append(date_creation["createdAt"])

    return created_date_movies


@pytest.fixture(scope="session")
def requester():
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_URL)


@pytest.fixture(scope="session")
def session():
    """
    Фикстура для создания HTTP-сессии.
    """
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="session")
def api_manager(session):
    """
    Фикстура для создания экземпляра ApiManager.
    """
    session.headers.update(HEADERS)
    AuthAPI(session).authenticate(USER_CREDS)
    #session.headers.update(auth_headers)

    return ApiManager(session)


@pytest.fixture
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()


@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session
    )

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin


@pytest.fixture(scope="function")
def creation_user_data(test_user):
    updated_data = test_user.copy()
    updated_data.update({
        "verified": True,
        "banned": False
    })
    return updated_data


@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    common_user = User(
        creation_user_data['email'],
        creation_user_data['password'],
        [Roles.USER.value],
        new_session
    )

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user


@pytest.fixture
def admin_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    admin_user = User(
        creation_user_data['email'],
        creation_user_data['password'],
        [Roles.ADMIN.value],
        new_session
    )

    super_admin.api.user_api.create_user(creation_user_data)
    admin_user.api.auth_api.authenticate(admin_user.creds)
    return admin_user
