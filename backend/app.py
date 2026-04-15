from flask import Flask, jsonify
from flask_restful import Api

from extensions import bcrypt, db, jwt, migrate
from resources import (
    LoginResource,
    NoteListResource,
    NoteResource,
    ProfileResource,
    RegisterResource,
)


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.DevelopmentConfig")

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    api = Api(app)
    api.add_resource(RegisterResource, "/auth/register")
    api.add_resource(LoginResource, "/auth/login")
    api.add_resource(ProfileResource, "/auth/profile")
    api.add_resource(NoteListResource, "/notes")
    api.add_resource(NoteResource, "/notes/<int:note_id>")

    @app.route("/", methods=["GET"])
    def health_check():
        return jsonify({"message": "Flask Notes API is running"})

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000)
