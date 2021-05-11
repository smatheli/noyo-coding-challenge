from flask import Blueprint, request, jsonify, make_response
from marshmallow import ValidationError

from app import db
from app.models.person import Person, PersonVersion
from app.schema.person import PersonSchema
from sqlalchemy import engine
from sqlalchemy.orm import scoped_session, sessionmaker

import sqlalchemy as sa


api = Blueprint('api', __name__, url_prefix='/api/v1/')


@api.route('/person', methods=['POST'])
def create_person():
    try:
        data = request.get_json()
        person_schema = PersonSchema()
        sess = scoped_session(sessionmaker(bind=engine))
        person = person_schema.load(data, session=sess)
        result = person_schema.dump(person.create())
        return make_response(jsonify({"person": result}), 200)
    except sa.exc.IntegrityError as err:
        return f'{err.orig.args[0]}: {err.orig.args[1]}', 500


@api.route('/person/<id>', methods=['GET'])
def get_person_by_id(id):
    get_person = Person.query.get(id)
    person_schema = PersonSchema()
    person = person_schema.dump(get_person)
    return make_response(jsonify({"person": person}))


@api.route('/person/<id>/<version>', methods=['GET'])
def get_versioned_person_by_id(id, version):
    validation_error = ValidationError({})
    try:
        person_versions = db.session.query(PersonVersion).filter_by(id=id).all()

        if not person_versions:
            validation_error.messages["id"] = "Id is not valid."
            raise validation_error
        elif len(person_versions) <= int(version):
            validation_error.messages["version"] = "Version is not valid."
            raise validation_error

        requested_version = person_versions[int(version)]
        person = {
            "first_name": requested_version.first_name,
            "last_name": requested_version.last_name,
            "email": requested_version.email,
            "age": requested_version.age,
        }
        return make_response(jsonify({"person": person}))
    except ValidationError as err:
        return err.messages, 500


@api.route('/person', methods=['GET'])
def get_all_persons():
    get_persons = Person.query.all()
    person_schema = PersonSchema(many=True)
    persons = person_schema.dump(get_persons)
    return make_response(jsonify({"persons": persons}))


@api.route('/person/<id>', methods=['PUT'])
def update_person_by_id(id):
    try:
        data = request.get_json()
        get_person = Person.query.get(id)

        if data.get('first_name'):
            get_person.first_name = data['first_name']
        if data.get('last_name'):
            get_person.last_name = data['last_name']
        if data.get('email'):
            get_person.email = data['email']
        if data.get('age'):
            get_person.age = data['age']

        db.session.add(get_person)
        db.session.commit()
        person_schema = PersonSchema(only=['first_name', 'last_name', 'email', 'age'])
        person = person_schema.dump(get_person)
        return make_response(jsonify({"person": person}))
    except ValidationError as err:
        return err.messages, 500


@api.route('/person/<id>', methods=['DELETE'])
def delete_person_by_id(id):
    validation_error = ValidationError({})
    try:
        get_person = Person.query.get(id)

        if not get_person:
            validation_error.messages["id"] = "Id is not valid."
            raise validation_error

        db.session.delete(get_person)
        db.session.commit()
        return make_response("", 204)
    except ValidationError as err:
        return err.messages, 500
