from sqlalchemy_continuum import make_versioned, version_class
from sqlalchemy.ext.declarative import declarative_base

from app import db

import sqlalchemy as sa


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
PersonVersion = version_class(Person)   # create version class for Person
