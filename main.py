import json
import logging
from datetime import datetime, timedelta
from typing import List, Tuple

import coloredlogs
from aiohttp import web
from fhirpy.base.resource import AbstractResource

from aidbox_python_sdk.main import create_app as _create_app
from aidbox_python_sdk.sdk import SDK
from aidbox_python_sdk.settings import Settings
from helpers.response import success_response, error_response
from resources.appointment.appointment import Appointment
from resources.resource import Resource
from resources.service_request.service_request import ServiceRequest
from resources.slot.slot import Slot

logger = logging.getLogger()
coloredlogs.install(level='DEBUG', fmt='%(asctime)s %(levelname)s %(message)s')

settings = Settings(**{})

with open('resources.json', 'r') as resource:
    resources: dict = json.loads(resource.read())

with open('seed.json', 'r') as seed:
    seeds: dict = json.loads(seed.read())

sdk = SDK(settings, resources=resources, seeds=seeds)


async def create_app():
    return await _create_app(settings, sdk, debug=True)


def is_required_args_present(requirement_args: list, args: list) -> bool:
    """ Проверяем запросе на наличие обязательные аргументы """
    if len(set(requirement_args) - set(args)) != 0:
        return False

    return True


@sdk.operation(methods=['POST'], path=['create_appointment'])
async def create_appointment(operation, request: dict):
    """
        Создание консилиума

        POST /create_appointment
    """
    requirement_args: list = ['name', 'begin_date', 'organisation_id', 'place']
    req: dict = request.get('resource', {})
    if not is_required_args_present(requirement_args, list(req.keys())):
        return error_response('Some of requirements fields not present', web)

    appointment: Resource = Appointment(sdk)
    slot: Resource = Slot(sdk)

    name: str = req.get('name')
    begin_date: str = req.get('begin_date').replace(' ', 'T')
    end_date: str = req.get('end_date').replace(' ', 'T')
    organisation_id: str = req.get('organisation_id')
    place: str = req.get('place')

    fields: dict = {
        'identifier': [{'use': 'official',
                        'value': name,
                        'assigner': {'resourceType': 'Organization', 'id': organisation_id, 'type': 'Organization'}
                        }],
        'description': place,
        'start': begin_date,
        'end': end_date,
        'participant': [
            {"actor": {'id': 'dfaa8925-f32e-4687-8fd0-272844cff544', 'resourceType': 'Patient'},
             "required": "required",
             "status": "accepted"
             },
        ],
        'status': 'pending',
        'created': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        'comment': 'Some comment',
    }
    slot_fields: dict = {
        'status': 'free',
        'overbooked': False,
        'comment': 'Some comment',
        'schedule': {
            'id': 'ad3f8065-b454-474c-8151-e85f202f18c5',
            'resourceType': 'Schedule'
        },
    }
    try:
        slots: List[dict] = []
        for _ in range(9):
            slot_fields['end'] = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S')
            slot_fields['start'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            slot_id: str = await slot.create(slot_fields)
            slots.append({'id': slot_id, 'resourceType': 'Slot'})

        fields['slot'] = slots
        appointment_id: str = await appointment.create(fields)
        return success_response({'id': appointment_id}, web)
    except BaseException as e:
        logger.error(str(e))
        return error_response(str(e), web)


@sdk.operation(methods=['POST'], path=['create_service_request'])
async def create_service_request(operation, request):
    """
        Создание заявки на консилиум

        POST /create_service_request
    """
    requirement_args = ['appointment_id', 'patient_id', 'condition_id']
    req: dict = request.get('resource', {})
    if not is_required_args_present(requirement_args, list(req.keys())):
        return error_response('Some of requirements fields not present', web)

    patient_id: str = req.get('patient_id')
    condition_id: str = req.get('condition_id')
    appointment_id: str = req.get('appointment_id')

    appointment: Resource = Appointment(sdk, appointment_id)
    service_request: Resource = ServiceRequest(sdk)

    fields: dict = {
        'supportingInfo': [
            {'id': 'ad3f8465-b454-494c-8351-e85f282f48c4', 'resourceType': 'Composition'},
        ],
        'authoredOn': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        'status': 'draft',
        'intent': "proposal",
        'subject': {'resourceType': 'Patient', 'id': patient_id},
        'requester': {'resourceType': 'Organization', 'id': '576bb080-cf42-401a-9be9-1fa09c49c372'},
        'reasonReference': [{'resourceType': 'Condition', 'id': condition_id}],
    }

    try:
        appointment_: AbstractResource = await appointment.get()
        slot_id, overbooked = await _get_free_slot(appointment_['slot'])

        if overbooked:
            await appointment.add_subfields(('slot', [{'id': slot_id, 'resourceType': 'Slot'}]))

        if fields.get('supportingInfo') is not None and isinstance(fields.get('supportingInfo'), list):
            fields['supportingInfo'].append({'id': slot_id, 'resourceType': 'Slot'})

        service_request_id: str = await service_request.create(fields)

        await appointment.add_fields({'basedOn': [{'resourceType': 'ServiceRequest',
                                                   'id': service_request_id}]})
    except BaseException as e:
        logger.error(str(e))
        return error_response(str(e), web)

    return success_response({'id': service_request_id}, web)


@sdk.operation(methods=['POST'], path=['move_service_request_to_appointment'])
async def move_service_request_to_appointment(operation, request):
    """
        Перемещение заявки между консилиумами

        POST /move_service_request_to_appointment
    """
    requirement_args = ['appointment_id', 'service_request_id']
    req: dict = request.get('resource', {})
    if not is_required_args_present(requirement_args, list(req.keys())):
        return error_response('Some of requirements fields not present', web)

    service_request_id: str = req.get('service_request_id')
    appointment_id: str = req.get('appointment_id')

    new_appointment: Resource = Appointment(sdk, appointment_id)
    service_request: Resource = ServiceRequest(sdk, service_request_id)

    try:
        """
            Нажожу консилиум по привязаной к нему заявке, 
            создаю экземпляр клясса с id найденого консилиума и удаляю привязку к заявке
        """
        old_appointment_: AbstractResource = (await Appointment.search(sdk, {'based_on': service_request_id}))[0]
        old_appointment: Resource = Appointment(sdk, old_appointment_.get('id'))
        await old_appointment.remove_fields(['basedOn'])

        """ Удаляю привязку к слоту старого консилиума """
        slot_id: str = await service_request.remove_slot()

        """Проверяем что это за слот, если overbooked, то удаляем, если нет, то меняем статус на free"""
        slot: Slot = Slot(sdk, slot_id)
        slot_: AbstractResource = await slot.get()
        if slot_.get('overbooked'):
            await old_appointment.remove_subfields(('slot', [slot_id]))
            await slot.delete()
        else:
            await slot.update(field='status', val='free')

        """ Приязываю заявку к новому консилиуму """
        await new_appointment.add_fields({'basedOn': [{'resourceType': 'ServiceRequest',
                                                       'id': service_request_id}]})

        """ Достаю слоты из нового консилиума и привязывю свободный к заявке """
        new_appointment_: AbstractResource = await new_appointment.get()

        slot_id, overbooked = await _get_free_slot(new_appointment_.get('slot'))
        if overbooked:
            await new_appointment.add_subfields(('slot', [{'id': slot_id, 'resourceType': 'Slot'}]))

        await service_request.add_subfields(('supportingInfo', [{'id': slot_id, 'resourceType': 'Slot'}]))
    except BaseException as e:
        return error_response(str(e), web)

    return success_response({}, web)


async def _get_free_slot(slots: List[dict]) -> Tuple[str, bool]:
    """Находим свободный слот, если есть такой, меняем у него статус на busy, если нет то создаем новый"""
    overbooked: bool = False
    slots: List[str] = await Slot.get_free(sdk, slots)
    if len(slots) > 0:
        slot: Slot = Slot(sdk, slots[0])
        await slot.update(field='status', val='busy')
    else:
        overbooked = True
        slot: Slot = Slot(sdk)
        await slot.create({
            'start': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'end': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S'),
            'status': 'busy',
            'overbooked': True,
            'comment': 'Some comment',
            'schedule': {
                'id': 'ad3f8065-b454-474c-8151-e85f202f18c5',
                'resourceType': 'Schedule'
            },
        })

    return slot.get_id(), overbooked
