from typing import List, Tuple

from aidboxpy import AsyncAidboxResource
from fhirpy.base.resource import AbstractResource

from aidbox_python_sdk.sdk import SDK
from resources.resource import Resource


class ServiceRequest(Resource):
    """Класс для работы с заявками"""

    def __init__(self, sdk: SDK, pk: str = None):
        super().__init__(pk, sdk)

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

    @staticmethod
    async def search(sdk: SDK, search: dict) -> AsyncAidboxResource:
        """Поиск по произвольным параметрам"""
        if len(search) == 0:
            raise AttributeError('Attribute: search, must not be empty.')

        try:
            resources: AsyncAidboxResource = await sdk.client.resources(ServiceRequest.__name__) \
                .search(**search) \
                .fetch()
            if len(resources) == 0:
                raise BaseException('Can not find service requests by given params')
        except BaseException as e:
            raise BaseException(e)

        return resources

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
