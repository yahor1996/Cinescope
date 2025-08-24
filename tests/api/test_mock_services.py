import datetime

import pytest
import pytz
import requests
from Cinescope.custom_requester.custom_requester import CustomRequester
from Cinescope.api.clients.api_manager import ApiManager
from Cinescope.constants.roles import Roles
from Cinescope.models.base_models import RegisterUserResponse, TestUser

import requests
from pydantic import BaseModel, Field
from datetime import datetime
from fastapi import FastAPI
from datetime import datetime, timedelta
from pytest_mock import mocker
from unittest.mock import Mock


# Модель Pydantic для ответа сервера worldclockapi
class WorldClockResponse(BaseModel):
    id: str = Field(alias="$id")  # Используем алиас для поля "$id"
    currentDateTime: str
    utcOffset: str
    isDayLightSavingsTime: bool
    dayOfTheWeek: str
    timeZoneName: str
    currentFileTime: int
    ordinalDate: str
    serviceResponse: None

    class Config:
        # Разрешаем использование алиасов при парсинге JSON
        allow_population_by_field_name = True


# Модель для запроса к сервису TodayIsHoliday
class DateTimeRequest(BaseModel):
    currentDateTime: str  # Формат: "2025-02-13T21:43Z"


# Модель для ответа от сервиса TodayIsHoliday
class WhatIsTodayResponse(BaseModel):
    message: str


# Функция выолняющая запрос в сервис worldclockapi для получения текущей даты
def get_worldclockap_time() -> WorldClockResponse:
    # Выполняем GET-запрос
    response = requests.get("http://worldclockapi.com/api/json/utc/now")  # Запрос в реальный сервис
    # Проверяем статус ответа
    assert response.status_code == 200, "Удаленный сервис недоступен"
    # Парсим JSON-ответ с использованием Pydantic модели
    return WorldClockResponse(**response.json())


# Создаем Stub для функции get_worldclockap_time
def stub_get_worldclockap_time():
    class StubWorldClockResponse:
        def __init__(self):
            self.currentDateTime = "2025-05-09T00:00Z"  # Фиксированная дата для Stub
    return StubWorldClockResponse()


#перед запсуком необходимо выполнить команду
#docker run -it --rm -p 8080:8080 --name wiremock wiremock/wiremock:3.12.0
def run_wiremock_worldclockap_time(self):
# Запуск WireMock сервера (если используется standalone, этот шаг можно пропустить)
    wiremock_url = "http://localhost:8080/__admin/mappings"
    mapping = {
        "request": {
            "method": "GET",
            "url": "/wire/mock/api/json/utc/now"  # Эмулируем запрос к worldclockapi
        },
        "response": {
            "status": 200,
            "body": '''{
                "$id": "1",
                "currentDateTime": "2025-03-08T00:00Z",
                "utcOffset": "00:00",
                "isDayLightSavingsTime": false,
                "dayOfTheWeek": "Wednesday",
                "timeZoneName": "UTC",
                "currentFileTime": 1324567890123,
                "ordinalDate": "2025-1",
                "serviceResponse": null
            }'''
        }
    }
    response = requests.post(wiremock_url, json=mapping)
    assert response.status_code == 201, "Не удалось настроить WireMock"


#Функция выполняющая запрос в Fake сервис worldclockapi для получения текущей даты
def get_fake_worldclockap_time() -> WorldClockResponse:
    # Выполняем GET-запрос
    response = requests.get("http://127.0.0.1:16001/fake/worldclockapi/api/json/utc/now")  #Запрос в реальный сервис
    # Проверяем статус ответа
    assert response.status_code == 200, "Удаленный сервис недоступен"
    # Парсим JSON-ответ с использованием Pydantic модели
    return  WorldClockResponse(**response.json())


class TestTodayIsHolidayServiceAPI:
    @pytest.mark.skip
    def test_what_is_today_BY_MOCK(self, mocker):
        # Создаем мок для функции get_worldclockap_time
        mocker.patch(
            "test_mock_services.get_worldclockap_time",
            # Указываем путь к функции в нашем модуле (формат файл.класс.метод)
            # либо имя_файла.имя_метода если он находится  вэтом же файле
            return_value=Mock(
                currentDateTime="2025-01-01T00:00Z"  # Фиксированная дата для возврата из мок функции "1 января"
            )
        )

        # Выполним тело предыдущего теста еще раз
        world_clock_response = get_worldclockap_time()  # = "2025-01-01T00:00Z"

        what_is_today_response = requests.post("http://127.0.0.1:16002/what_is_today",
                                               data=DateTimeRequest(
                                                   currentDateTime=world_clock_response.currentDateTime).model_dump_json()
                                               )

        # Проверяем статус ответа от тестируемого сервиса
        assert what_is_today_response.status_code == 200, "Удаленный сервис недоступен"
        # Парсим JSON-ответ от тестируемого сервиса с использованием Pydantic модели
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())

        assert what_is_today_data.message == "Новый год", "ДОЛЖЕН БЫТЬ НОВЫЙ ГОД!"

    # Тест с использованием Stub
    @pytest.mark.skip
    def test_what_is_today_BY_STUB(self, monkeypatch):
        # Подменяем реальную функцию get_worldclockap_time на Stub
        monkeypatch.setattr("test_mock_services.get_worldclockap_time", stub_get_worldclockap_time)
        # или же можем просто напрямую взять значение из Stub world_clock_response = stub_get_worldclockap_time()

        # Выполним тело предыдущего теста еще раз
        world_clock_response = get_worldclockap_time()  # Произойдет вызов Stub, возвращающего "2025-01-01T00:00Z"

        # Выполняем запрос к тестируемому сервису
        what_is_today_response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            data=DateTimeRequest(currentDateTime=world_clock_response.currentDateTime).model_dump_json()
        )

        # Проверяем статус ответа от тестируемого сервиса
        assert what_is_today_response.status_code == 200, "Удаленный сервис недоступен"
        # Парсим JSON-ответ от тестируемого сервиса с использованием Pydantic модели
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        # Проверяем, что ответ соответствует ожидаемому
        assert what_is_today_data.message == "День Победы", "ДОЛЖЕН БЫТЬ ДЕНЬ ПОБЕДЫ!"

    @pytest.mark.skip
    def test_what_is_today_BY_WIREMOCK(self):  # Данный тест максимально похож на базовый
        # запускаем наш мок сервер
        run_wiremock_worldclockap_time(self)

        # Выполняем запрос к WireMock (имитация worldclockapi)
        world_clock_response = requests.get("http://localhost:8080/wire/mock/api/json/utc/now")
        assert world_clock_response.status_code == 200, "Удаленный сервис недоступен"
        # Парсим JSON-ответ с использованием Pydantic модели
        current_date_time = WorldClockResponse(**world_clock_response.json()).currentDateTime

        # Выполняем запрос к тестируемому сервису what_is_today
        what_is_today_response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            data=DateTimeRequest(currentDateTime=current_date_time).model_dump_json()
        )

        # Проверяем статус ответа от тестируемого сервиса
        assert what_is_today_response.status_code == 200, "Удаленный сервис недоступен"
        # Парсим JSON-ответ от тестируемого сервиса с использованием Pydantic модели
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        # Проверяем, что ответ соответствует ожидаемому
        assert what_is_today_data.message == "Международный женский день", "8 марта же?"

    @pytest.mark.skip
    # worldclockap
    def test_worldclockap(self):  # проверка работоспособности сервиса worldclockap
        world_clock_response = get_worldclockap_time()
        # Выводим текущую дату и время
        current_date_time = world_clock_response.currentDateTime
        print(f"Текущая дата и время: {current_date_time=}")

        assert current_date_time == datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%MZ"), "Дата не совпадает"

    @pytest.mark.skip
    def test_what_is_today(self):  # проверка работоспособности Fake сервиса what_is_today
        # Запрашиваем текущее время у сервиса worldclockap
        world_clock_response = get_worldclockap_time()

        what_is_today_response = requests.post("http://127.0.0.1:16002/what_is_today",
                                               data=DateTimeRequest(
                                                   currentDateTime=world_clock_response.currentDateTime).model_dump_json()
                                               )

        # Проверяем статус ответа от тестируемогосервиса
        assert what_is_today_response.status_code == 200, "Удаленный сервис недоступен"
        # Парсим JSON-ответ от тестируемого сервиса с использованием Pydantic модели
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        # Проводим валидацию ответа тестируемого сервиса
        assert what_is_today_data.message == "Сегодня нет праздников в России.", "Сегодня нет праздника!"

    @pytest.mark.skip
    # worldclockap
    def test_fake_worldclockap(self):  # проверка работоспособности сервиса worldclockap
        world_clock_response = get_fake_worldclockap_time()
        # Выводим текущую дату и время
        current_date_time = world_clock_response.currentDateTime
        print(f"Текущая дата и время: {current_date_time=}")

        assert current_date_time == datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%MZ"), "Дата не совпадает"

    @pytest.mark.skip
    def test_fake_what_is_today(self):  # проверка работоспособности Fake сервиса what_is_today
        # Запрашиваем текущее время у сервиса worldclockap
        world_clock_response = get_fake_worldclockap_time()

        what_is_today_response = requests.post("http://127.0.0.1:16002/what_is_today",
                                               data=DateTimeRequest(
                                                   currentDateTime=world_clock_response.currentDateTime).model_dump_json()
                                               )

        # Проверяем статус ответа от тестируемого сервиса
        assert what_is_today_response.status_code == 200, "Удаленный сервис недоступен"
        # Парсим JSON-ответ от тестируемого сервиса с использованием Pydantic модели
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())

        assert what_is_today_data.message == "Сегодня нет праздников в России.", "Сегодня нет праздника!"