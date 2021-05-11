#!/usr/bin/env python
"""Application entry point"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config) -> Flask:
    # create application
    app = Flask(__name__)
    app.config.from_object(config_class)

    # bind database handler to Flask app
    db.init_app(app)
    migrate.init_app(app, db)

    # register api endpoints with Flask app
    from app.routes.person import api
    app.register_blueprint(api)

    return app
