from abc import ABC, abstractmethod
from typing import Tuple, List

from aidboxpy import AsyncAidboxResource
from fhirpy.base.resource import AbstractResource

from aidbox_python_sdk.sdk import SDK


class Resource(ABC):
    """Базрвый класс для ресурсов"""

    _pk: str
    _sdk: SDK

    def __init__(self, pk: str, sdk: SDK):
        self._sdk = sdk
        self._pk = pk

    @abstractmethod
    async def create(self, fields: dict) -> str:
        """Создание нового ресурса"""
        pass

    @abstractmethod
    async def get(self) -> AbstractResource:
        """Получить ресурса по идентификатору"""
        pass

    @staticmethod
    async def search(sdk: SDK, search: dict) -> AsyncAidboxResource:
        """Поиск по произвольным параметрам"""
        pass

    @abstractmethod
    async def add_fields(self, fields: dict) -> object:
        """Добавление полей в ресурс"""
        pass

    @abstractmethod
    async def add_subfields(self, fields: Tuple[str, List[dict]]) -> object:
        """Добавление вложенных полей в ресурс"""
        pass

    @abstractmethod
    async def remove_fields(self, fields: List[str]) -> object:
        """Удаление полей из ресурса"""
        pass

    @abstractmethod
    async def remove_subfields(self, fields: Tuple[str, List[str]]) -> object:
        """
            Удаление вложенных полей из ресурса
            :param fields ('supportingInfo', ['4c1736cc-4186-4c5c-afd8-8ae070da033b'])
        """
        pass

    @abstractmethod
    async def delete(self) -> object:
        """Удаляем запись"""
        pass

    @classmethod
    def get_id(cls) -> str:
        """Возвращаем идентификатор"""
        return cls._pk

    @classmethod
    def set_id(cls, pk: str):
        """Записываем идентификатор"""
        cls._pk = pk
