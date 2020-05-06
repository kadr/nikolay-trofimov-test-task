from typing import Tuple, List

from aidboxpy import AsyncAidboxResource
from fhirpy.base.resource import AbstractResource

from aidbox_python_sdk.sdk import SDK
from resources.resource import Resource


class Slot(Resource):
    """Класс для работы со слотами"""

    def __init__(self, sdk: SDK, pk: str = None):
        super().__init__(sdk, pk)

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

    async def update(self, field: str, val) -> object:
        """Обновление значения поля"""
        if self._pk is None:
            raise AttributeError('Id is not present')
        try:
            slot: AbstractResource = await self.get()
            slot[field] = val

            instance: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **slot,
            )
            await instance.save()

        except BaseException as e:
            raise BaseException(e)

        return self

    @staticmethod
    async def search(sdk: SDK, search: dict, resource_name: str = None) -> AsyncAidboxResource:
        """Поиск по произвольным параметрам"""
        if resource_name is None:
            resource_name = Slot.__name__

        return await super().search(sdk, resource_name, search)

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

    async def is_free(self) -> bool:
        """Проверка слота на доступоность"""
        if self._pk is None:
            raise AttributeError('Id is not present')

        slot: AbstractResource = await self.get()
        if slot.status == 'free':
            return True

        return False

    async def is_overbook(self) -> bool:
        """Проверка слота на доступоность"""
        if self._pk is None:
            raise AttributeError('Id is not present')

        slot: AbstractResource = await self.get()
        if slot.overbook:
            return True

        return False

    @staticmethod
    async def get_free(sdk: SDK, slots: List[dict]) -> List[str]:
        free_slots: List[str] = []
        for slot in slots:
            slot_: AbstractResource = await sdk.client.resources('Slot').get(id=slot.get('id'))
            if slot_.status == 'free':
                free_slots.append(slot_.id)

        return free_slots
