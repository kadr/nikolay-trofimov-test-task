from typing import Tuple, List

from aidboxpy import AsyncAidboxResource
from fhirpy.base.resource import AbstractResource

from aidbox_python_sdk.sdk import SDK
from resources.resource import Resource


class Slot(Resource):
    """Класс для работы со слотами"""

    def __init__(self, sdk: SDK, pk: str = None):
        super().__init__(pk, sdk)

    async def create(self, fields: dict) -> str:
        """Создание нового слота"""
        try:
            slot: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **fields
            )
            await slot.save()
            self._pk = slot.id

            return self._pk
        except BaseException as e:
            raise BaseException(e)

    async def get(self) -> AbstractResource:
        """Получить слот по идентификатору"""
        if self._pk is None:
            raise AttributeError('Id is not present')

        try:
            slot: AbstractResource = await self._sdk.client.resources(self.__class__.__name__).get(id=self._pk)
            del slot['resourceType']

            return slot
        except BaseException as e:
            raise BaseException(e)

    @staticmethod
    async def search(sdk: SDK, search: dict) -> AsyncAidboxResource:
        """Поиск по произвольным параметрам"""
        if len(search) == 0:
            raise AttributeError('Attribute search must not be empty.')

        try:
            resources: AsyncAidboxResource = await sdk.client.resources(Slot.__name__) \
                .search(**search) \
                .fetch()
            if len(resources) == 0:
                raise BaseException('Can not find appointments by given params')
        except BaseException as e:
            raise BaseException(e)

        return resources

    async def add_fields(self, fields: dict) -> object:
        """Добавление полей в слот"""
        if self._pk is None:
            raise AttributeError('Id is not present')

        try:
            slot: AbstractResource = await self.get()

            instance: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **slot,
                **fields
            )
            await instance.save()

        except BaseException as e:
            raise BaseException(e)

        return self

    async def add_subfields(self, fields: Tuple[str, List[dict]]) -> object:
        """
            Добавления вложенных полей в слота
            :param fields ('supportingInfo', [
                {'id': '4c1736cc-4186-4c5c-afd8-8ae070da033b', 'resourceType': 'Slot'},
                ...
            ])
        """
        if self._pk is None:
            raise AttributeError('Id is not present')

        try:
            slot: AbstractResource = await self.get()

            key, items = fields
            if slot.get(key) is not None and isinstance(slot.get(key), list):
                for item in items:
                    slot.get(key).append(item)

            instance: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **slot,
            )
            await instance.save()

        except BaseException as e:
            raise BaseException(e)

        return self

    async def remove_fields(self, fields: List[str]) -> object:
        """Удаление полей из слота"""
        if self._pk is None:
            raise AttributeError('Id is not present')

        try:
            slot: AbstractResource = await self.get()
            for field in fields:
                del slot[field]

            instance: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **slot
            )
            await instance.save()

        except BaseException as e:
            raise BaseException(e)

        return self

    async def remove_subfields(self, fields: Tuple[str, List[str]]) -> object:
        """
            Удаление вложенных полей из слота
            :param fields ('supportingInfo', ['4c1736cc-4186-4c5c-afd8-8ae070da033b'])
        """
        if self._pk is None:
            raise AttributeError('Id is not present')

        try:
            slot: AbstractResource = await self.get()

            key, ids = fields
            field: List[dict] = slot.get(key)
            if field is not None and isinstance(field, list):
                for index, item in enumerate(field):
                    id_ = item.get('id')
                    if id_ is not None and id_ in ids:
                        del slot[key][index]

            instance: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **slot
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
