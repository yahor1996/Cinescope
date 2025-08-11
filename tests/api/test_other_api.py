from Cinescope.conftest.conftest import *
from datetime import datetime, timedelta
from pytz import timezone
from Cinescope.db_requester.models import MovieDBModel, AccountTransactionTemplate
from Cinescope.utils.data_generator import DataGenerator
from sqlalchemy.orm import Session

class TestMoviesDB:
    def test_create_delete_movie(self, super_admin, db_session: Session):
        # как бы выглядел SQL запрос
        """SELECT id, "name", price, description, image_url, "location", published, rating, genre_id, created_at
           FROM public.movies
           WHERE name='Test Moviej1h8qss9s5';"""

        movie_name = f"Test Movie{DataGenerator.generate_random_movie_name()}"
        movies_from_db = db_session.query(MovieDBModel).filter(MovieDBModel.name == movie_name)

        # проверяем что до начала тестирования фильма с таким названием нет
        assert movies_from_db.count() == 0, "В базе уже присутствует фильм с таким названием"

        movie_data = {
            "name": movie_name,
            "price": 500,
            "description": "Описание тестового фильма",
            "location": "MSK",
            "published": True,
            "genreId": 3
        }
        response = super_admin.api.movies_api.create_movie(movie_data)
        assert response.status_code == 201, "Фильм должен успешно создаться"
        response = response.json()

        # проверяем после вызова api_manager.movies_api.create_movie в базе появился наш фильм
        movies_from_db = db_session.query(MovieDBModel).filter(MovieDBModel.name == movie_name)
        assert movies_from_db.count() == 1, "В базе уже присутствует фильм с таким названием"

        movie_from_db = movies_from_db.first()
        # можете обратить внимание, что в базе данных есть поле created_at которое мы не здавали явно
        # наш сервис сам его заполнил. проверим что он заполнил его верно с погрешностью в 5 минут
        assert movie_from_db.created_at >= (datetime.now(timezone('UTC')).replace(tzinfo=None) - timedelta(minutes=5)), "Сервис выставил время создания с большой погрешностью"

        # Берем айди фильма который мы только что создали и  удаляем его из базы через апи
        # Удаляем фильм
        delete_response = super_admin.api.movies_api.delete_movie(movie_id=response["id"])
        assert delete_response.status_code == 200, "Фильм должен успешно удалиться"

        # проверяем что в конце тестирования фильма с таким названием действительно нет в базе
        movies_from_db = db_session.query(MovieDBModel).filter(MovieDBModel.name == movie_name)
        assert movies_from_db.count() == 0, "Фильм не был удален из базы!"



    def test_accounts_transaction_template(self, db_session: Session):
        # ====================================================================== Подготовка к тесту
        # Создаем новые записи в базе данных (чтоб точно быть уверенными что в базе присутствуют данные для тестирования)

        stan = AccountTransactionTemplate(user=f"Stan_{DataGenerator.generate_random_name()}", balance=1000)
        bob = AccountTransactionTemplate(user=f"Bob_{DataGenerator.generate_random_name()}", balance=500)

        # Добавляем записи в сессию
        db_session.add_all([stan, bob])
        # Фиксируем изменения в базе данных
        db_session.commit()

        def transfer_money(session, from_account, to_account, amount):
            # пример функции выполняющей транзакцию
            # представим что она написана на стороне тестируемого сервиса
            # и вызывая метод transfer_money, мы какбудтобы делем запрос в api_manager.movies_api.transfer_money
            """
            Переводит деньги с одного счета на другой.
            :param session: Сессия SQLAlchemy.
            :param from_account_id: ID счета, с которого списываются деньги.
            :param to_account_id: ID счета, на который зачисляются деньги.
            :param amount: Сумма перевода.
            """
            # Получаем счета
            from_account = session.query(AccountTransactionTemplate).filter_by(user=from_account).one()
            to_account = session.query(AccountTransactionTemplate).filter_by(user=to_account).one()

            # Проверяем, что на счете достаточно средств
            if from_account.balance < amount:
                raise ValueError("Недостаточно средств на счете")

            # Выполняем перевод
            from_account.balance -= amount
            to_account.balance += amount

            # Сохраняем изменения
            session.commit()

        # ====================================================================== Тест
        # Проверяем начальные балансы
        assert stan.balance == 1000
        assert bob.balance == 500

        try:
            # Выполняем перевод 200 единиц от stan к bob
            transfer_money(db_session, from_account=stan.user, to_account=bob.user, amount=200)

            # Проверяем, что балансы изменились
            assert stan.balance == 800
            assert bob.balance == 700

        except Exception as e:
            # Если произошла ошибка, откатываем транзакцию
            db_session.rollback()  # откат всех введеных нами изменений
            pytest.fail(f"Ошибка при переводе денег: {e}")

        finally:
            # Удаляем данные для тестирования из базы
            db_session.delete(stan)
            db_session.delete(bob)
            # Фиксируем изменения в базе данных
            db_session.commit()