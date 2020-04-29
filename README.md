### Тестовое задание для Николая Трофимова

Необходимо реализовать rest api на https://github.com/Aidbox/aidbox-python-sdk для работы с сущностями Консилиум (Appointment) и Заявка на консилиум (ServiceRequest). 
 
 Должны быть реализованы методы:
- создание консилиума. На вход принимает название консилиума и дату/время проведения, идентификатор организации (Organization), текстовое описание места («этаж2 кабинет 3») 
 - создания Заявки на консилиум. На вход принимает идентификатор пациента (Patient) и идентификатор Консилиума (Appointment), идентификатор Заболивания пациента (Condition).
- перемещения заявки между консилиумами

#### Создание консилиума
POST /create_appointment
```json
{
    "name": "Some name", 
    "begin_date": "2020-12-12 12:12:12",
    "organisation_id": "34283a80-7ea5-4f2a-8f3b-1718a5084199",
    "place": "2 этаж, 120 кабинет"
}
```
#### Создание заявки на консилиум
POST /create_service_request
```json
{
  "appointment_id":  "fcde8fad-4136-4dc8-bee5-b18a80004fa8",
  "patient_id":  "dcf9da43-da55-4bd0-87bd-b17ee712400f",
  "condition_id": "dfaa8925-f32e-4687-8fd0-272844cff544"
}
```
#### Перемещение заявки между консилиумами
POST /move_service_request_to_appointment
```json
{
  "service_request_id": "34283a80-7ea5-4f2a-8f3b-1718a5084199",
  "appointment_id": "fcde8fad-4136-4dc8-bee5-b18a80004fa8"
}
```