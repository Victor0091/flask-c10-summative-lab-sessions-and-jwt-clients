from marshmallow import Schema, ValidationError, fields, validates


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)


class NoteSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    mood = fields.Str(missing=None)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    user_id = fields.Int(dump_only=True)

    @validates("title")
    def validate_title(self, value):
        if not value.strip():
            raise ValidationError("Title must not be empty")

    @validates("content")
    def validate_content(self, value):
        if not value.strip():
            raise ValidationError("Content must not be empty")
