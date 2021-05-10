from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_continuum import make_versioned, version_class
from sqlalchemy.ext.declarative import declarative_base
from marshmallow import fields, validates_schema, ValidationError
from marshmallow_sqlalchemy import ModelSchema

import re
import sqlalchemy as sa

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/person'
db = SQLAlchemy(app)

#########
# Model #
#########
make_versioned(user_cls=None)
Base = declarative_base()


class Person(db.Model, Base):
    __versioned__ = {}
    __tablename__ = 'person'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), unique=False, nullable=False)
    last_name = db.Column(db.String(50), unique=False, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    age = db.Column(db.Integer, unique=False, nullable=False)

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except sa.exc.IntegrityError as err:
            raise err

    def __init__(self, first_name, last_name, email, age):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.age = age

    def __repr__(self):
        return f"Id: {self.id}"


sa.orm.configure_mappers()              # configure models
db.create_all()                         # create initial tables and database
PersonVersion = version_class(Person)   # create version class for Person


##########
# Schema #
##########
class PersonSchema(ModelSchema):
    class Meta:
        model = Person
        # exclude = ['versions']

    id = fields.Number(dump_only=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    email = fields.String(required=True)
    age = fields.Number(required=True)

    @validates_schema
    def validate_person(self, data, **kwargs):
        person_info = data
        validation_error = ValidationError({})
        found_error = False

        if "first_name" not in person_info or person_info["first_name"] == "":
            validation_error.messages["first_name"] = "First name field is blank."
            found_error = True

        if "last_name" not in person_info or person_info["last_name"] == "":
            validation_error.messages["last_name"] = "Last name field is blank."
            found_error = True

        if "email" not in person_info or person_info["email"] == "":
            validation_error.messages["email"] = "Email field is blank."
            found_error = True
        elif not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", person_info["email"]):
            validation_error.messages["email"] = "Invalid email address."
            found_error = True

        if "age" not in person_info or person_info["age"] == "":
            validation_error.messages["age"] = "Age field is blank."
            found_error = True

        if found_error:
            raise validation_error


#############
# Endpoints #
#############
@app.route('/api/v1/person', methods=['POST'])
def create_person():
    try:
        data = request.get_json()
        person_schema = PersonSchema()
        person = person_schema.load(data)
        result = person_schema.dump(person.create())
        return make_response(jsonify({"person": result}), 200)
    except sa.exc.IntegrityError as err:
        return f'{err.orig.args[0]}: {err.orig.args[1]}', 500


@app.route('/api/v1/person/<id>', methods=['GET'])
def get_person_by_id(id):
    get_person = Person.query.get(id)
    person_schema = PersonSchema()
    person = person_schema.dump(get_person)
    return make_response(jsonify({"person": person}))


@app.route('/api/v1/person/<id>/<version>', methods=['GET'])
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


@app.route('/api/v1/person', methods=['GET'])
def get_all_persons():
    get_persons = Person.query.all()
    person_schema = PersonSchema(many=True)
    persons = person_schema.dump(get_persons)
    return make_response(jsonify({"persons": persons}))


@app.route('/api/v1/person/<id>', methods=['PUT'])
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


@app.route('/api/v1/person/<id>', methods=['DELETE'])
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
