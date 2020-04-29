import asyncio
import coloredlogs
import logging
import sqlalchemy as sa
import time
from aidboxpy import AsyncAidboxResource
from aiohttp import web
from datetime import datetime
from fhirpy.base.resource import AbstractResource
from sqlalchemy.sql.expression import select, insert

from aidbox_python_sdk.handlers import routes
from aidbox_python_sdk.main import create_app as _create_app
from aidbox_python_sdk.sdk import SDK
from aidbox_python_sdk.settings import Settings

logger = logging.getLogger()
coloredlogs.install(level='DEBUG', fmt='%(asctime)s %(levelname)s %(message)s')

settings = Settings(**{})
resources = {
    'Client': {
        'SPA': {
            'secret': '123456',
            'grant_types': ['password']
        }
    },
    'User':
        {
            'superadmin':
                {
                    'email': 'superadmin@example.com',
                    'password': '12345678',
                }
        },
    'AccessPolicy':
        {
            'superadmin':
                {
                    'engine': 'json-schema',
                    'schema': {
                        'required': ['user']
                    }
                }
        },
}
seeds = {
    'Patient':
        {
            'dfaa8925-f32e-4687-8fd0-272844cff544':
                {
                    'name':
                        [
                            {
                                'use': 'official',
                                'family': 'Hauck852',
                                'given': ['Alayna598'],
                                'prefix': ['Ms.']
                            }
                        ],
                    'gender': 'female',
                },
            'dfaa8925-f32e-4687-8fd0-272844cff545':
                {
                    'name':
                        [
                            {
                                'use': 'official',
                                'family': 'Doe12',
                                'given': ['John46'],
                                'prefix': ['Ms.']
                            }
                        ]
                }
        },
    'Contract':
        {
            'e9a3ce1d-745d-4fe1-8e97-807a820e6151': {},
            'e9a3ce1d-745d-4fe1-8e97-807a820e6152': {},
            'e9a3ce1d-745d-4fe1-8e97-807a820e6153': {},
        }
}
sdk = SDK(settings, resources=resources, seeds=seeds)


async def create_app():
    return await _create_app(settings, sdk, debug=True)


@sdk.subscription('Appointment')
async def appointment_sub(event):
    """
    POST /Appointment
    """
    await asyncio.sleep(5)
    return await _appointment_sub(event)


async def _appointment_sub(event):
    participants = event['resource']['participant']
    patient_id = next(
        p['actor']['id']
        for p in participants if p['actor']['resourceType'] == 'Patient'
    )
    patient = await sdk.client.resources('Patient').get(id=patient_id)
    patient_name = '{} {}'.format(
        patient['name'][0]['given'][0], patient['name'][0]['family']
    )
    appointment_dates = 'Start: {:%Y-%m-%d %H:%M}, end: {:%Y-%m-%d %H:%M}'.format(
        datetime.fromisoformat(event['resource']['start']),
        datetime.fromisoformat(event['resource']['end'])
    )
    logging.info('*' * 40)
    if event['action'] == 'create':
        logging.info('{}, new appointment was created.'.format(patient_name))
        logging.info(appointment_dates)
    elif event['action'] == 'update':
        if event['resource']['status'] == 'booked':
            logging.info('{}, appointment was updated.'.format(patient_name))
            logging.info(appointment_dates)
        elif event['resource']['status'] == 'cancelled':
            logging.info('{}, appointment was cancelled.'.format(patient_name))
    logging.debug('`Appointment` subscription handler')
    logging.debug('Event: {}'.format(event))


@sdk.operation(
    methods=['POST', 'PATCH'],
    path=['signup', 'register', {
        "name": "date"
    }, {
              "name": "test"
          }]
)
def signup_register_op(operation, request):
    """
    POST /signup/register/21.02.19/testvalue
    PATCH /signup/register/22.02.19/patchtestvalue
    """
    logging.debug('`signup_register_op` operation handler')
    logging.debug('Operation data: %s', operation)
    logging.debug('Request: %s', request)
    return web.json_response(
        {
            'success': 'Ok',
            'request': request['route-params']
        }
    )


@sdk.operation(methods=['GET'], path=['Patient', '$weekly-report'], public=True)
@sdk.operation(methods=['GET'], path=['Patient', '$daily-report'])
async def daily_patient_report(operation, request):
    """
    GET /Patient/$weekly-report
    GET /Patient/$daily-report
    """
    patients = sdk.client.resources('Patient')
    async for p in patients:
        logging.debug(p.serialize())
    logging.debug('`daily_patient_report` operation handler')
    logging.debug('Operation data: %s', operation)
    logging.debug('Request: %s', request)
    return web.json_response(
        {
            'type': 'report',
            'success': 'Ok',
            'msg': 'Response from APP'
        }
    )


@routes.get('/db_tests')
async def db_tests(request):
    db = sdk.db
    app = db.App.__table__
    app_res = {'type': 'app', 'resources': {'User': {}, }}
    unique_id = 'abc{}'.format(time.time())
    test_statements = [
        insert(app).values(
            id=unique_id, txid=123, status='created', resource=app_res
        ).returning(app.c.id),
        app.update().where(app.c.id == unique_id).values(
            resource=app.c.resource.op('||')({
                'additional': 'property'
            })
        ),
        app.select().where(app.c.id == unique_id),
        app.select().where(app.c.status == 'recreated'),
        select([app.c.resource['type'].label('app_type')]),
        app.select().where(app.c.resource['resources'].has_key('User')),
        select([app.c.id]).where(app.c.resource['type'].astext == 'app'),
        select([sa.func.count(app.c.id)]).where(
            app.c.resource.contains({"type": "app"})
        ),
        # TODO: got an error for this query.
        # select('*').where(app.c.resource['resources'].has_all(array(['User', 'Client']))),
    ]
    for statement in test_statements:
        result = await db.alchemy(statement)
        logging.debug('Result:\n%s', result)
    return web.json_response({})


def is_required_args_present(requirement_args: list, args: list) -> bool:
    """ Проверяем запросе на наличие обязательные аргументы """
    if len(set(requirement_args) - set(args)) != 0:
        return False

    return True


def success_response(data: dict):
    """Успешный ответ"""
    return web.json_response({'success': True, 'message': '', **data})


def error_response(message: str):
    """Не успешный ответ"""
    return web.json_response({'success': False, 'message': message})


@sdk.operation(methods=['POST'], path=['create_appointment'])
async def create_appointment(operation, request: dict):
    """
        Создание консилиума

        POST /create_appointment
    """
    requirement_args: list = ['name', 'begin_date', 'organisation_id', 'place']
    req: dict = request.get('resource', {})
    if not is_required_args_present(requirement_args, list(req.keys())):
        return error_response('Some of requirements fields not present')

    name: str = req.get('name')
    begin_date: str = req.get('begin_date').replace(' ', 'T')
    end_date: str = req.get('end_date').replace(' ', 'T')
    organisation_id: str = req.get('organisation_id')
    place: str = req.get('place')

    try:
        appointment: AbstractResource = sdk.client.resource(
            resource_type='Appointment',
            identifier=[{'use': 'official',
                         'value': name,
                         'assigner': {'display': f'Organization/{organisation_id}',
                                      'resourceType': 'Organization',
                                      'id': organisation_id,
                                      'type': 'Organization'}
                         }],
            description=place,
            start=begin_date,
            end=end_date,
            participant=[],
            status='pending',
            created=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        )
        await appointment.save()
    except BaseException as e:
        return error_response(str(e))

    return success_response({'id': appointment.id})


@sdk.operation(methods=['POST'], path=['create_service_request'])
async def create_service_request(operation, request):
    """
        Создание заявки на консилиум

        POST /create_service_request
    """
    requirement_args = ['appointment_id', 'patient_id', 'condition_id']
    req: dict = request.get('resource', {})
    if not is_required_args_present(requirement_args, list(req.keys())):
        return error_response('Some of requirements fields not present')

    patient_id: str = req.get('patient_id')
    condition_id: str = req.get('condition_id')
    appointment_id: str = req.get('appointment_id')

    try:
        condition: AbstractResource = sdk.client.resource(
            resource_type='ServiceRequest',
            status='active',
            intent="order",
            subject={'display': f'Patient/{patient_id}', 'resourceType': 'Patient', 'id': patient_id},
            requester={'display': f'Patient/{patient_id}',
                       'resourceType': 'Patient', 'id': patient_id
                       },
            reasonReference=[{'display': f'Condition/{condition_id}',
                              'resourceType': 'Condition',
                              'id': condition_id}],
            authoredOn=datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        )
        await condition.save()

        appointment_: AbstractResource = await sdk.client.resources('Appointment').get(id=appointment_id)
        appointment_['resource_type'] = appointment_['resourceType']
        del appointment_['resourceType']

        appointment: AbstractResource = sdk.client.resource(
            **appointment_,
            basedOn=[{'display': f'ServiceRequest/{condition.id}',
                      'resourceType': 'ServiceRequest',
                      'id': condition.id}]
        )
        await appointment.save()
    except BaseException as e:
        return error_response(str(e))

    return success_response({'id': condition.id})


@sdk.operation(methods=['POST'], path=['move_service_request_to_appointment'])
async def move_service_request_to_appointment(operation, request):
    """
        Перемещение заявки между консилиумами

        POST /move_service_request_to_appointment
    """
    requirement_args = ['appointment_id', 'service_request_id']
    req: dict = request.get('resource', {})
    if not is_required_args_present(requirement_args, list(req.keys())):
        return error_response('Some of requirements fields not present')

    service_request_id: str = req.get('service_request_id')
    appointment_id: str = req.get('appointment_id')

    try:
        old_appointment: AsyncAidboxResource = await sdk.client.resources('Appointment') \
            .search(based_on=service_request_id) \
            .fetch()
        if len(old_appointment) > 0:
            old_appointment = old_appointment[0]
            old_appointment['resource_type'] = old_appointment['resourceType']
            del old_appointment['resourceType']
            del old_appointment['basedOn']
            appointment: AbstractResource = sdk.client.resource(
                **old_appointment
            )
            await appointment.save()
        else:
            return error_response('No records found')
        new_appointment: AbstractResource = await sdk.client.resources('Appointment').get(id=appointment_id)
        new_appointment['resource_type'] = new_appointment['resourceType']
        del new_appointment['resourceType']
        appointment: AbstractResource = sdk.client.resource(
            **new_appointment,
            basedOn=[{'display': f'ServiceRequest/{service_request_id}',
                      'resourceType': 'ServiceRequest',
                      'id': service_request_id}]
        )
        await appointment.save()
    except BaseException as e:
        return error_response(str(e))

    return success_response({'id': appointment.id})
