from pydantic import BaseModel
from Cinescope.constants.roles import Roles
from Cinescope.utils.data_generator import DataGenerator
from venv import logger


class UserData(BaseModel):
    email: str
    fullName: str
    password: str
    passwordRepeat: str
    roles: list[str]


def get_user_data():
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


def test_user_data():
    user = UserData(**get_user_data())  # Проверяем возможность конвертации данных и соответствия типов данных с помощью Pydantic
    logger.info(f"{user.email=} {user.fullName=} {user.password=} {user.passwordRepeat=} {user.roles=}")  # а также возможность удобного взаимодействия
