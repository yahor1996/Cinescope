import pytest
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ValidationError
from Cinescope.constants.roles import Roles
from Cinescope.utils.data_generator import DataGenerator
from venv import logger


class UserData(BaseModel):
    email: str = Field(..., min_length=21, max_length=21, description="Электронная почта")
    fullName: str = Field(..., description="Полное имя")
    password: str = Field(..., min_length=8, max_length=20, description="Пароль")
    passwordRepeat: str = Field(..., min_length=8, max_length=20)
    roles: list[Roles]
    banned: Optional[bool] = None
    verified: Optional[bool] = None

    @field_validator("email") # Кастомный валидатор для проверки символа '@' в email
    def check_email(cls, value: str) -> str:
        # Проверяем что почта содержит символ "@"
        if '@' not in value:
            raise ValueError("email must contains '@'")
        return value


@pytest.fixture(scope="function")
def test_user():
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": [Roles.USER]
    }


@pytest.fixture(scope="function")
def creation_user_data(test_user):
    """
    Фикстура для создания пользователя.
    """
    updated_data = test_user.copy()
    updated_data.update({
        "verified": True,
        "banned": False
    })
    return updated_data



def test_user_data(test_user, creation_user_data):
    # Проверяем возможность конвертации данных и соответствия типов данных с помощью Pydantic
    test_user = UserData(**test_user)

    # Проверяем возможность удобного взаимодействия
    logger.info(
        f"{test_user.email=} "
        f"{test_user.fullName=} "
        f"{test_user.password=} "
        f"{test_user.passwordRepeat=} "
        f"{test_user.roles=} "
        f"{test_user.banned=} "
        f"{test_user.verified=}"
    )

    json_test_user = test_user.model_dump_json(exclude_unset=True)
    logger.info(json_test_user)

    # Проверяем возможность конвертации данных и соответствия типов данных с помощью Pydantic
    creation_user = UserData(**creation_user_data)

    # Проверяем возможность удобного взаимодействия
    logger.info(
        f"{creation_user.email=} "
        f"{creation_user.fullName=} "
        f"{creation_user.password=} "
        f"{creation_user.passwordRepeat=} "
        f"{creation_user.roles=} "
        f"{creation_user.banned=} "
        f"{creation_user.verified=}"
    )

    json_creation_user = creation_user.model_dump_json()
    logger.info(json_creation_user)