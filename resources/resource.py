from abc import ABC, abstractmethod
from typing import Tuple, List

from aidboxpy import AsyncAidboxResource
from fhirpy.base.resource import AbstractResource

from aidbox_python_sdk.sdk import SDK


class Resource(ABC):
    """Базрвый класс для ресурсов"""

    _pk: str
    _sdk: SDK

    def __init__(self, sdk: SDK, pk: str):
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

    async def update(self, field: str, val) -> object:
        """Обновление значения поля"""
        pass

    @staticmethod
    async def search(sdk: SDK, resource_name: str, search: dict) -> AsyncAidboxResource:
        """Поиск по произвольным параметрам"""
        if len(search) == 0:
            raise AttributeError('Attribute search must not be empty.')

        try:
            resources: AsyncAidboxResource = await sdk.client.resources(resource_name) \
                .search(**search) \
                .fetch()
            if len(resources) == 0:
                raise BaseException('Can not find appointments by given params')
        except BaseException as e:
            raise BaseException(e)

        return resources

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

    def get_id(self) -> str:
        """Возвращаем идентификатор"""
        return self._pk

    def set_id(cls, pk: str):
        """Записываем идентификатор"""
        cls._pk = pk
