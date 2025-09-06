import time

from faker import Faker
import pytest
import requests

from api.clients.api_manager import ApiManager
from api.clients.auth_api import AuthAPI
from Cinescope.constants.constants import BASE_URL, REGISTER_ENDPOINT, USER_CREDS, HEADERS, MOVIES_ENDPOINT
from Cinescope.constants.roles import Roles
from Cinescope.models.base_models import TestUser
from Cinescope.resources.user_creds import SuperAdminCreds
from Cinescope.entities.user import User
from Cinescope.custom_requester.custom_requester import CustomRequester
from Cinescope.utils.data_generator import DataGenerator
from urllib.parse import urlencode
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from playwright.sync_api import sync_playwright

faker = Faker()

@pytest.fixture(scope="function")
def test_user() -> TestUser:
    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return TestUser(
         email=random_email,
         fullName=random_name,
         password=random_password,
         passwordRepeat=random_password,
         roles=[Roles.USER]
    )


@pytest.fixture(scope="function")
def registered_user(requester, test_user):
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    response = requester.send_request(
        method="POST",
        endpoint=REGISTER_ENDPOINT,
        data=test_user,
        expected_status=[200, 201]
    )
    response_data = response.json()
    registered_user = test_user.model_copy(update={"id": response_data["id"]})
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
        expected_status=[200, 201]
    )

    created_movie = response.json()
    yield created_movie

    # Очистка после теста
    movie_id = created_movie["id"]
    super_admin.api.movies_api.send_request(
        method="DELETE",
        endpoint=f"{MOVIES_ENDPOINT}/{movie_id}",
        expected_status=[200, 201]
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
        expected_status=[200, 201]
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
        expected_status=[200, 201]
    )

    created_review = response.json()
    yield created_review

    # Очистка после теста
    super_admin.api.movies_api.send_request(
        method="DELETE",
        endpoint=f"{MOVIES_ENDPOINT}/{movie_id}/reviews",
        data=created_review,
        expected_status=[200, 201]
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
        expected_status=[200, 201]
    )

    new_review = response.json()
    return new_review


@pytest.fixture(scope="function")
def hidden_review(super_admin, created_movie, created_review):
    """
    Фикстура для создания скрытого отзыва к фильму
    """
    params_review = {
        "movieId": created_movie["id"],
        "userId": created_review["userId"]
    }

    response = super_admin.api.movies_api.hide_review(params_review)
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

    # Определение параметров
    params = {
        'pageSize': random_page_size,
        'page': random_page,
        'minPrice': random_min_price,
        'maxPrice': random_max_price,
        'locations': 'MSK,SPB',
        'published': 'true',
        'createdAt': 'asc'
    }

    # Формирование строки запроса
    query_string = urlencode(params)

    # Возвращение строки с вопросительным знаком
    return f'?{query_string}'


@pytest.fixture(scope="function")
def get_movies_created_date(common_user, params_movies):
    """
    Фикстура для получения даты создания фильмов.
    """
    response = common_user.api.movies_api.send_request(
        method="GET",
        endpoint=f"{MOVIES_ENDPOINT}{params_movies}",
        expected_status=[200, 201]
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
    """
    Фикстура для создания сессии пользователя.
    """
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
    """
    Фикстура для создания пользователя с правами супер админа.
    """
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
    """
    Фикстура для создания пользователя.
    """
    updated_data = test_user.model_copy(update={"verified": True, "banned": False})
    return updated_data


@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    """
    Фикстура для создания пользователя с обычными правами.
    """
    new_session = user_session()

    common_user = User(
        creation_user_data.email,
        creation_user_data.password,
        [Roles.USER.value],
        new_session
    )

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user


@pytest.fixture
def admin_user(user_session, super_admin, creation_user_data):
    """
    Фикстура для создания пользователя с правами админа.
    """
    new_session = user_session()
    admin_data = creation_user_data.model_copy(update={"roles": [Roles.ADMIN]})

    admin_user = User(
        admin_data.email,
        admin_data.password,
        admin_data.roles,
        new_session
    )

    response = super_admin.api.user_api.create_user(admin_data)
    created_admin = response.json()

    data = {
        "roles": [Roles.ADMIN.value],
        "verified": True,
        "banned": False
    }

    super_admin.api.user_api.update_user(created_admin['id'], data)
    admin_user.api.auth_api.authenticate(admin_user.creds)

    return admin_user


#Оставим эти данные тут для наглядности. но не стоит хранить креды в гитлабе. они должны быть заданы через env
HOST = "80.90.191.123"
PORT = 31200
DATABASE_NAME = "db_movies"
USERNAME = "postgres"
PASSWORD = "AmwFrtnR2"

engine = create_engine(f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}") # Создаем движок (engine) для подключения к базе данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Создаем фабрику сессий

@pytest.fixture(scope="module")
def db_session():
    """
    Фикстура, которая создает и возвращает сессию для работы с базой данных.
    После завершения теста сессия автоматически закрывается.
    """
    # Создаем новую сессию
    db_session = SessionLocal()
    # Возвращаем сессию в тест
    yield db_session
    # Закрываем сессию после завершения теста
    db_session.close()


@pytest.fixture
def delay_between_retries():
    time.sleep(2)  # Задержка в 2 секунды\ это не обязательно но
    yield          # нужно понимать что такая возможность имеется


DEFAULT_UI_TIMEOUT = 30000  # Пример значения таймаута

@pytest.fixture(scope="session")  # Браузер запускается один раз для всей сессии
def browser(playwright):
    browser = playwright.chromium.launch(headless=False)  # headless=True для CI/CD, headless=False для локальной разработки - смотреть pytest.ini
    yield browser  # yield возвращает значение фикстуры, выполнение теста продолжится после yield
    browser.close()  # Браузер закрывается после завершения всех тестов


@pytest.fixture(scope="function")  # Контекст создается для каждого теста
def context(browser):
    context = browser.new_context()
    context.tracing.start(screenshots=True, snapshots=True, sources=True)  # Трассировка для отладки
    context.set_default_timeout(DEFAULT_UI_TIMEOUT)  # Установка таймаута по умолчанию
    yield context  # yield возвращает значение фикстуры, выполнение теста продолжится после yield
    context.close()  # Контекст закрывается после завершения теста


@pytest.fixture(scope="function")  # Страница создается для каждого теста
def page(context):
    page = context.new_page()
    yield page  # yield возвращает значение фикстуры, выполнение теста продолжится после yield
    page.close()  # Страница закрывается после завершения теста