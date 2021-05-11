from app import create_app, db
from config import TestConfig

import json
import pytest


@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


def test_create_person(client):
    first_name = 'John'
    last_name = 'Appleseed'
    email = 'john.appleseed@me.com'
    age = 42

    response = _create_person(client, first_name, last_name, email, age)
    data = json.loads(response.data.decode())

    assert response.status_code == 201
    assert first_name == data['person']['first_name']
    assert last_name == data['person']['last_name']
    assert email == data['person']['email']
    assert age == data['person']['age']


def test_get_person_by_id(client):
    first_name = 'John'
    last_name = 'Appleseed'
    email = 'john.appleseed@me.com'
    age = 42

    response = client.get('/api/v1/person/1')
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert not data['person']

    _create_person(client, first_name, last_name, email, age)
    response = client.get('/api/v1/person/1')
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert data['person']['id'] == 1


def test_get_versioned_person_by_id(client):
    first_name = 'John'
    updated_first_name = "Johnny"
    last_name = 'Appleseed'
    email = 'john.appleseed@me.com'
    age = 42

    response = client.get('/api/v1/person/1/1')
    data = json.loads(response.data.decode())

    assert response.status_code == 500
    assert data['id'] == 'Id is not valid.'

    _create_person(client, first_name, last_name, email, age)
    response = client.get('/api/v1/person/1/1')
    data = json.loads(response.data.decode())

    assert response.status_code == 500
    assert data['version'] == 'Version is not valid.'

    _update_person_by_id(client, updated_first_name, 1)
    response = client.get('/api/v1/person/1/1')
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert updated_first_name == data['person']['first_name']

    response = client.get('/api/v1/person/1/0')
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert first_name == data['person']['first_name']


def test_get_all_persons(client):
    first_name_1 = 'John'
    last_name_1 = 'Appleseed'
    email_1 = 'john.appleseed@me.com'
    age_1 = 42

    first_name_2 = 'Tom'
    last_name_2 = 'Hanks'
    email_2 = 'tom.hanks@gmail.com'
    age_2 = 60

    response = client.get('/api/v1/person')
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert len(data['persons']) == 0

    _create_person(client, first_name_1, last_name_1, email_1, age_1)
    response = client.get('/api/v1/person')
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert len(data['persons']) == 1

    _create_person(client, first_name_2, last_name_2, email_2, age_2)
    response = client.get('/api/v1/person')
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert len(data['persons']) == 2


def test_update_person_by_id(client):
    first_name = 'John'
    updated_first_name = "Johnny"
    last_name = 'Appleseed'
    email = 'john.appleseed@me.com'
    age = 42

    response = client.put('/api/v1/person/1')
    data = json.loads(response.data.decode())

    assert response.status_code == 500
    assert data['id'] == 'Id is not valid.'

    _create_person(client, first_name, last_name, email, age)
    response = _update_person_by_id(client, updated_first_name, 1)
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert updated_first_name == data['person']['first_name']


def test_delete_person_by_id(client):
    first_name = 'John'
    last_name = 'Appleseed'
    email = 'john.appleseed@me.com'
    age = 42

    response = client.delete('/api/v1/person/1')
    data = json.loads(response.data.decode())

    assert response.status_code == 500
    assert data['id'] == 'Id is not valid.'

    _create_person(client, first_name, last_name, email, age)
    response = client.get('/api/v1/person')
    data = json.loads(response.data.decode())

    assert len(data['persons']) == 1

    response = client.delete('/api/v1/person/1')

    assert response.status_code == 204

    response = client.get('/api/v1/person')
    data = json.loads(response.data.decode())

    assert response.status_code == 200
    assert len(data['persons']) == 0

    response = client.get('/api/v1/person/1/0')
    data = json.loads(response.data.decode())

    # Check to ensure we can still get initial version of person
    assert response.status_code == 200
    assert first_name == data['person']['first_name']


def _create_person(client, first_name, last_name, email, age):
    return client.post(
        '/api/v1/person',
        data=json.dumps(dict(
            first_name=first_name,
            last_name=last_name,
            email=email,
            age=str(age)
        )),
        content_type='application/json'
    )


def _update_person_by_id(client, updated_first_name, id):
    return client.put(
        f'/api/v1/person/{id}',
        data=json.dumps(dict(first_name=updated_first_name)),
        content_type='application/json'
    )
