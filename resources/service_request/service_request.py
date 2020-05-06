from typing import List, Tuple

from aidboxpy import AsyncAidboxResource
from fhirpy.base.resource import AbstractResource

from aidbox_python_sdk.sdk import SDK
from resources.resource import Resource


class ServiceRequest(Resource):
    """Класс для работы с заявками"""

    def __init__(self, sdk: SDK, pk: str = None):
        super().__init__(sdk, pk)

    async def create(self, fields: dict) -> str:
        """Создание новой заявки"""
        try:
            instance: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **fields
            )
            await instance.save()

            return instance.id
        except BaseException as e:
            raise BaseException(e)

    async def get(self) -> AbstractResource:
        """Получить заявку по идентификатору"""
        if self._pk is None:
            raise AttributeError('Id is not present')

        try:
            service_request: AbstractResource = await self._sdk.client.resources(self.__class__.__name__).get(
                id=self._pk)
            del service_request['resourceType']

            return service_request
        except BaseException as e:
            raise BaseException(e)

    async def update(self, field: str, val) -> object:
        """Обновление значения поля"""
        if self._pk is None:
            raise AttributeError('Id is not present')
        try:
            service_request: AbstractResource = await self.get()
            service_request[field] = val

            instance: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **service_request,
            )
            await instance.save()

        except BaseException as e:
            raise BaseException(e)

        return self

    @staticmethod
    async def search(sdk: SDK, search: dict, resource_name: str = None) -> AsyncAidboxResource:
        """Поиск по произвольным параметрам"""
        if resource_name is None:
            resource_name = ServiceRequest.__name__

        return await super().search(sdk, resource_name, search)

    async def add_fields(self, fields: dict) -> object:
        """Добавления полей в заявку"""
        if self._pk is None:
            raise AttributeError('Id is not present')

        try:
            service_request: AbstractResource = await self.get()

            instance: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **service_request,
                **fields
            )
            await instance.save()

        except BaseException as e:
            raise BaseException(e)

        return self

    async def add_subfields(self, fields: Tuple[str, List[dict]]) -> object:
        """
            Добавления вложенных полей в заявку
            :param fields ('supportingInfo', [
                {'id': '4c1736cc-4186-4c5c-afd8-8ae070da033b', 'resourceType': 'Slot'},
                ...
            ])
        """
        if self._pk is None:
            raise AttributeError('Id is not present')

        try:
            service_request: AbstractResource = await self.get()

            key, items = fields
            if service_request.get(key) is not None and isinstance(service_request.get(key), list):
                for item in items:
                    service_request.get(key).append(item)

            instance: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **service_request,
            )
            await instance.save()

        except BaseException as e:
            raise BaseException(e)

        return self

    async def remove_fields(self, fields: List[str]) -> object:
        """Удаление полей из заявки"""
        if self._pk is None:
            raise AttributeError('Id is not present')

        try:
            service_request: AbstractResource = await self.get()
            for field in fields:
                del service_request[field]

            instance: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **service_request
            )
            await instance.save()

        except BaseException as e:
            raise BaseException(e)

        return self

    async def remove_subfields(self, fields: Tuple[str, List[str]]) -> object:
        """
            Удаление вложенных полей из заявки
            :param fields ('supportingInfo', ['4c1736cc-4186-4c5c-afd8-8ae070da033b'])
        """
        if self._pk is None:
            raise AttributeError('Id is not present')

        try:
            service_request: AbstractResource = await self.get()

            key, ids = fields
            field: List[dict] = service_request.get(key)
            if field is not None and isinstance(field, list):
                for index, item in enumerate(field):
                    id_ = item.get('id')
                    if id_ is not None and id_ in ids:
                        del service_request[key][index]

            instance: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **service_request
            )
            await instance.save()

        except BaseException as e:
            raise BaseException(e)

        return self

    async def remove_slot(self) -> str:
        if self._pk is None:
            raise AttributeError('Id is not present')
        pk: str = ''
        try:
            service_request: AbstractResource = await self.get()
            for index, item in enumerate(service_request.get('supportingInfo')):
                if item.get('resourceType') == 'Slot':
                    pk = item.get('id')
                    del service_request['supportingInfo'][index]

            instance: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **service_request
            )
            await instance.save()
        except BaseException as e:
            raise BaseException(e)

        return pk

    async def delete(self) -> object:
        """Удаляем запись"""
        if self._pk is None:
            raise AttributeError('Id is not present')

        instance: AbstractResource = self._sdk.client.resource(
            resource_type=self.__class__.__name__,
            id=self._pk
        )
        await instance.delete()

        return self
