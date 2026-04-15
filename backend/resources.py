from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from marshmallow import ValidationError

from extensions import bcrypt, db
from models import Note, User
from schemas import NoteSchema, UserSchema

user_schema = UserSchema()
note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)


def get_current_user():
    identity = get_jwt_identity()
    return User.query.filter_by(username=identity).first()


def owner_or_404(note, user):
    if note is None:
        return {"message": "Note not found"}, 404
    if note.owner != user:
        return {"message": "Forbidden"}, 403
    return None


class RegisterResource(Resource):
    def post(self):
        payload = request.get_json() or {}
        username = payload.get("username")
        password = payload.get("password")

        if not username or not password:
            return {"message": "Username and password are required."}, 400

        if User.query.filter_by(username=username).first():
            return {"message": "Username already exists."}, 409

        password_digest = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(username=username, password_digest=password_digest)
        db.session.add(user)
        db.session.commit()

        return user_schema.dump(user), 201


class LoginResource(Resource):
    def post(self):
        payload = request.get_json() or {}
        username = payload.get("username")
        password = payload.get("password")

        if not username or not password:
            return {"message": "Username and password are required."}, 400

        user = User.query.filter_by(username=username).first()
        if user is None or not bcrypt.check_password_hash(user.password_digest, password):
            return {"message": "Invalid username or password."}, 401

        access_token = create_access_token(identity=user.username)
        return {
            "access_token": access_token,
            "user": user_schema.dump(user),
        }, 200


class ProfileResource(Resource):
    @jwt_required()
    def get(self):
        user = get_current_user()
        return user_schema.dump(user), 200


class NoteListResource(Resource):
    @jwt_required()
    def get(self):
        user = get_current_user()
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        per_page = min(per_page, 50)

        pagination = Note.query.filter_by(owner=user).order_by(Note.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            "notes": notes_schema.dump(pagination.items),
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }, 200

    @jwt_required()
    def post(self):
        user = get_current_user()
        payload = request.get_json() or {}

        try:
            note_data = note_schema.load(payload)
        except ValidationError as exc:
            return {"errors": exc.messages}, 400

        note = Note(owner=user, **note_data)
        db.session.add(note)
        db.session.commit()

        return note_schema.dump(note), 201


class NoteResource(Resource):
    @jwt_required()
    def get(self, note_id):
        user = get_current_user()
        note = Note.query.get(note_id)
        error = owner_or_404(note, user)
        if error:
            return error
        return note_schema.dump(note), 200

    @jwt_required()
    def put(self, note_id):
        user = get_current_user()
        note = Note.query.get(note_id)
        error = owner_or_404(note, user)
        if error:
            return error

        payload = request.get_json() or {}
        try:
            note_data = note_schema.load(payload, partial=True)
        except ValidationError as exc:
            return {"errors": exc.messages}, 400

        for key, value in note_data.items():
            setattr(note, key, value)

        db.session.commit()
        return note_schema.dump(note), 200

    @jwt_required()
    def delete(self, note_id):
        user = get_current_user()
        note = Note.query.get(note_id)
        error = owner_or_404(note, user)
        if error:
            return error

        db.session.delete(note)
        db.session.commit()
        return {"message": "Note deleted successfully."}, 200
