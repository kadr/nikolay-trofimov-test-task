from typing import Tuple, List

from aidboxpy import AsyncAidboxResource
from fhirpy.base.resource import AbstractResource

from aidbox_python_sdk.sdk import SDK
from resources.resource import Resource


class Appointment(Resource):
    """Класс для работы с консилиумами"""

    def __init__(self, sdk: SDK, pk: str = None):
        super().__init__(sdk, pk)

    async def create(self, fields: dict) -> str:
        """Создание нового консилиума"""
        try:
            appointment: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **fields
            )
            await appointment.save()
            self._pk = appointment.id

            return self._pk
        except BaseException as e:
            raise BaseException(e)

    async def get(self) -> AbstractResource:
        """Получить консилиум по идентификатору"""

        if self._pk is None:
            raise AttributeError('Id is not present')

        try:
            appointment: AbstractResource = await self._sdk.client.resources(self.__class__.__name__).get(id=self._pk)
            del appointment['resourceType']

            return appointment
        except BaseException as e:
            raise BaseException(e)

    async def update(self, field: str, val) -> object:
        """Обновление значения поля"""
        if self._pk is None:
            raise AttributeError('Id is not present')
        try:
            appointment: AbstractResource = await self.get()
            appointment[field] = val

            instance: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **appointment,
            )
            await instance.save()

        except BaseException as e:
            raise BaseException(e)

        return self

    @staticmethod
    async def search(sdk: SDK, search: dict, resource_name: str = None) -> AsyncAidboxResource:
        """Поиск по произвольным параметрам"""
        if resource_name is None:
            resource_name = Appointment.__name__

        return await super(Appointment, Appointment).search(sdk, resource_name, search)

    async def add_fields(self, fields: dict) -> object:
        """Добавление полей в консилиум"""
        if self._pk is None:
            raise AttributeError('Id is not present')

        try:
            appointment: AbstractResource = await self.get()

            instance: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **appointment,
                **fields
            )
            await instance.save()

        except BaseException as e:
            raise BaseException(e)

        return self

    async def add_subfields(self, fields: Tuple[str, List[dict]]) -> object:
        """
            Добавления вложенных полей в консилиум
            :param fields ('supportingInfo', [
                {'id': '4c1736cc-4186-4c5c-afd8-8ae070da033b', 'resourceType': 'Slot'},
                ...
            ])
        """
        if self._pk is None:
            raise AttributeError('Id is not present')

        try:
            appointment: AbstractResource = await self.get()

            key, items = fields
            if appointment.get(key) is not None and isinstance(appointment.get(key), list):
                for item in items:
                    appointment.get(key).append(item)

            instance: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **appointment,
            )
            await instance.save()

        except BaseException as e:
            raise BaseException(e)

        return self

    async def remove_fields(self, fields: List[str]) -> object:
        """Удаление полей из консилиума"""
        if self._pk is None:
            raise AttributeError('Id is not present')

        try:
            appointment: AbstractResource = await self.get()
            for field in fields:
                del appointment[field]

            instance: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **appointment
            )
            await instance.save()

        except BaseException as e:
            raise BaseException(e)

        return self

    async def remove_subfields(self, fields: Tuple[str, List[str]]) -> object:
        """
            Удаление вложенных полей из консилиума
            :param fields ('supportingInfo', ['4c1736cc-4186-4c5c-afd8-8ae070da033b'])
        """
        if self._pk is None:
            raise AttributeError('Id is not present')

        try:
            appointment: AbstractResource = await self.get()

            key, ids = fields
            field: List[dict] = appointment.get(key)
            if field is not None and isinstance(field, list):
                for index, item in enumerate(field):
                    id_ = item.get('id')
                    if id_ is not None and id_ in ids:
                        del appointment[key][index]

            instance: AbstractResource = self._sdk.client.resource(
                resource_type=self.__class__.__name__,
                **appointment
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
