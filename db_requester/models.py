import pytest
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Integer, ForeignKey, text
from sqlalchemy.orm import declarative_base, sessionmaker
from Cinescope.conftest.conftest import SessionLocal
from Cinescope.utils.data_generator import DataGenerator


Base = declarative_base()

#Модель базы данных для пользователя
class UserDBModel(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    email = Column(String)
    full_name = Column(String)
    password = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    verified = Column(Boolean)
    banned = Column(Boolean)
    roles = Column(String)


@pytest.fixture(scope="module")
def db_session():
    """
    Фикстура с областью видимости module.
    Тестовые данные создаются один раз для всех тестов в модуле.
    """
    session = SessionLocal()

    # Создаем тестовые данные
    test_user = UserDBModel(
        id = "test_id",
        email = DataGenerator.generate_random_email(),
        full_name = DataGenerator.generate_random_name(),
        password = DataGenerator.generate_random_password(),
        created_at = datetime.datetime.now(),
        updated_at = datetime.datetime.now(),
        verified = False,
        banned = False,
        roles = "{USER}"
    )
    session.add(test_user) #добавляем обьект в базу данных
    session.commit() #сохраняем изменения для всех остальных подключений

    yield session # можете запустить тесты в дебаг режиме и поставить тут брекпойнт
                  # зайдите в базу и убедитесь что нывй обьект был создан

	#код ниже выполнится после всех запущеных тестов
    session.delete(test_user) # Удаляем тестовые данные
    session.commit() # сохраняем изменения для всех остальных подключений
    session.close() #завершем сессию (отключаемся от базы данных)



class MovieDBModel(Base):
    """
    Модель для таблицы movies.
    """
    __tablename__ = 'movies'  # Имя таблицы в базе данных

    # Поля таблицы
    id = Column(String, primary_key=True)  # Уникальный идентификатор фильма
    name = Column(String, nullable=False)  # Название фильма
    description = Column(String)  # Описание фильма
    price = Column(Integer, nullable=False)  # Цена фильма
    genre_id = Column(String, ForeignKey('genres.id'), nullable=False)  # Ссылка на жанр
    image_url = Column(String)  # Ссылка на изображение
    location = Column(String)  # Локация фильма (например, "MSK")
    rating = Column(Integer)  # Рейтинг фильма
    published = Column(Boolean)  # Опубликован ли фильм
    created_at = Column(DateTime)  # Дата создания записи