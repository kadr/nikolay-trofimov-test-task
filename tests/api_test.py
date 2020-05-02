import json
from datetime import datetime

import pytest
from fhirpy.base.resource import AbstractResource

from aidbox_python_sdk.main import create_app
from aidbox_python_sdk.sdk import SDK
from aidbox_python_sdk.settings import Settings
from api.appointment.appointment import Appointment
from api.service_request.service_request import ServiceRequest


class TestApiClasses:
    """"""

    _appointment_id: str = ''
    _service_request_id: str = ''
    _organisation_id: str = ''
    _appointment_fields: dict = {}
    _service_request_fields: dict = {}
    _sdk: SDK = None
    _appointment: Appointment = None
    _service_request: ServiceRequest = None
    _settings: Settings = None

    def setup_class(self):
        self._settings = Settings(**{})
        with open('resources.json', 'r') as resource:
            resources: dict = json.loads(resource.read())

        self._sdk = SDK(self._settings, resources=resources, seeds={})

        self._appointment_fields = {
            'identifier': [{'use': 'official',
                            'value': 'Some name',
                            'assigner': {'resourceType': 'Organization',
                                         'id': self._organisation_id,
                                         'type': 'Organization'}
                            }],
            'description': 'Some place',
            'start': '2020-12-12T12:12:12',
            'end': '2020-12-12T12:12:13',
            'participant': [
                {"actor": {'id': 'dfaa8925-f32e-4687-8fd0-272844cff544',
                           'resourceType': 'Patient'},
                 "required": "required",
                 "status": "accepted"
                 },
            ],
            'status': 'pending',
            'created': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'comment': 'Some comment',
            'slot': [
                {'id': 'ad3f8066-b464-474c-8151-e85f202f18c4', 'resourceType': 'Slot'}
            ],
            'supportingInformation': [
                {'id': 'ad3f8064-b484-474c-8851-e853202f18c5',
                 'resourceType': 'DiagnosticReport'},
                {'id': 'ad3f8066-b464-474c-8151-e85f202f18c4', 'resourceType': 'Slot'}
            ]
        }

        self._service_request_fields = {
            'supportingInfo': [
                {'id': 'ad3f8465-b454-494c-8351-e85f282f48c4', 'resourceType': 'Composition'},
                {'id': 'cd3f8266-d464-474c-7151-s85f502f18m2', 'resourceType': 'Slot'}
            ],
            'authoredOn': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'status': 'draft',
            'intent': "proposal",
            'subject': {'resourceType': 'Patient', 'id': 'dfaa8925-f32e-4687-8fd0-272844cff544'},
            'requester': {'resourceType': 'Organization', 'id': '576bb080-cf42-401a-9be9-1fa09c49c372'},
            'reasonReference': [{'resourceType': 'Condition', 'id': '0adceaf4-36a7-44cb-b938-b84a3da0fb1f'}],
        }

    def teardown_class(self):
        del self._organisation_id
        del self._service_request_id
        del self._service_request_fields
        del self._service_request
        del self._appointment_id
        del self._appointment_fields
        del self._appointment
        del self._sdk

    @pytest.fixture(scope='class', autouse=True)
    async def init_sdk(self):
        await create_app(self._settings, self._sdk, debug=True)

    @pytest.fixture()
    async def create_appointment(self):
        if self._appointment is None:
            self._appointment = Appointment(self._sdk)
            await self._appointment.create(self._appointment_fields)

    @pytest.fixture()
    async def create_service_request(self):
        if self._service_request is None:
            self._service_request = ServiceRequest(self._sdk)
            await self._service_request.create(self._service_request_fields)

    @pytest.mark.asyncio
    async def test_create_appointment(self):
        appointment: Appointment = Appointment(self._sdk)
        pk: str = await appointment.create(self._appointment_fields)
        assert isinstance(pk, str) and len(pk) > 0

    @pytest.mark.asyncio
    async def test_add_fields_appointment(self, create_appointment, create_service_request):
        await self._appointment.add_fields({'basedOn': [{'resourceType': 'ServiceRequest',
                                                         'id': self._service_request.get_id()}]})
        appointment: AbstractResource = Appointment.search({'based_on': self._service_request.get_id()})[0]

        assert appointment.id == self._appointment.get_id()

    @pytest.mark.asyncio
    async def test_remove_fields_appointment(self, create_appointment, create_service_request):
        await self._appointment.remove_fields(['basedOn'])
        with pytest.raises(BaseException):
            assert Appointment.search({'based_on': self._service_request.get_id()})

    @pytest.mark.asyncio
    async def test_get_appointment(self, create_appointment):
        appointment = await self._appointment.get()

        assert appointment.id == self._appointment.get_id()

    @pytest.mark.asyncio
    async def test_delete_appointment(self, create_appointment):
        await self._appointment.delete()
        with pytest.raises(BaseException):
            assert self._appointment.get()
