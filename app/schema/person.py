from marshmallow import fields, validates_schema, ValidationError
from marshmallow_sqlalchemy import ModelSchema

from app.models.person import Person

import re


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
