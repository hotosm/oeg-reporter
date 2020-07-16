from flask_cors import CORS
from flask import Flask
from flasgger import Swagger
from flask_marshmallow import Marshmallow


ma = Marshmallow()


def create_app():
    app = Flask(__name__)

    # Load configuration options from environment
    app.config.from_object("server.config.EnvironmentConfig")

    # Database configuration
    ma.init_app(app)

    # Add paths to API endpoints
    add_api_endpoints(app)

    # Swagger configuration
    Swagger(app)

    # Enables CORS on all API routes, meaning API is callable from anywhere
    CORS(app)
    return app


def add_api_endpoints(app):

    from server.api.git.resources import GitDocumentApi

    app.add_url_rule(
        "/git/",
        view_func=GitDocumentApi.as_view("create_git_document"),
        methods=["POST"],
    )
    app.add_url_rule(
        "/git/",
        view_func=GitDocumentApi.as_view("update_git_document"),
        methods=["PATCH"],
    )
