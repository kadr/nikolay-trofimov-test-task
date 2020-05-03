from typing import Tuple, List

from aidboxpy import AsyncAidboxResource
from fhirpy.base.resource import AbstractResource

from aidbox_python_sdk.sdk import SDK
from resources.resource import Resource


class Appointment(Resource):
    """Класс для работы с консилиумами"""

    def __init__(self, sdk: SDK, pk: str = None):
        super().__init__(pk, sdk)

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

    @staticmethod
    async def search(sdk: SDK, search: dict) -> AsyncAidboxResource:
        """Поиск по произвольным параметрам"""
        if len(search) == 0:
            raise AttributeError('Attribute search must not be empty.')

        try:
            resources: AsyncAidboxResource = await sdk.client.resources(Appointment.__name__) \
                .search(**search) \
                .fetch()
            if len(resources) == 0:
                raise BaseException('Can not find appointments by given params')
        except BaseException as e:
            raise BaseException(e)

        return resources

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
