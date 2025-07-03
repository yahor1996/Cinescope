import random
import string
from faker import Faker

faker = Faker()


class DataGenerator:

    @staticmethod
    def generate_random_email():
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"kek{random_string}@gmail.com"


    @staticmethod
    def generate_random_name():
        return f"{faker.first_name()} {faker.last_name()}"

    @staticmethod
    def generate_random_password():
        """
        Генерация пароля, соответствующего требованиям:
        - Минимум 1 буква.
        - Минимум 1 цифра.
        - Допустимые символы.
        - Длина от 8 до 20 символов.
        """
        # Гарантируем наличие хотя бы одной буквы и одной цифры
        letters = random.choice(string.ascii_letters)  # Одна буква
        digits = random.choice(string.digits)  # Одна цифра

        # Дополняем пароль случайными символами из допустимого набора
        special_chars = "?@#$%^&*|:"
        all_chars = string.ascii_letters + string.digits + special_chars
        remaining_length = random.randint(6, 18)  # Остальная длина пароля
        remaining_chars = ''.join(random.choices(all_chars, k=remaining_length))

        # Перемешиваем пароль для рандомизации
        password = list(letters + digits + remaining_chars)
        random.shuffle(password)

        return ''.join(password)


    @staticmethod
    def generate_random_movie_name():
        return f"Егор_Тест_{faker.name()}"


    @staticmethod
    def generate_random_movie_price():
        return faker.random_int(min=100, max=1000)


    @staticmethod
    def generate_random_movie_description():
        return f"Душноватый_фильм_{faker.name()}"


    @staticmethod
    def generate_random_movie_genreId():
        return faker.random_int(min=1, max=4)


    @staticmethod
    def generate_random_movie_rating():
        return faker.random_int(min=1, max=5)


    @staticmethod
    def generate_random_movie_review_text():
        return f"Хороший_фильм_{faker.name()}"


    @staticmethod
    def generate_random_page_size():
        return faker.random_int(min=1, max=10)


    @staticmethod
    def generate_random_page():
        return faker.random_int(min=1, max=2)


    @staticmethod
    def generate_random_min_price():
        return faker.random_int(min=1, max=200)

    @staticmethod
    def generate_random_max_price():
        return faker.random_int(min=201, max=1000)

