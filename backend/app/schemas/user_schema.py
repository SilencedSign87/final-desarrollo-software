from marshmallow import Schema, fields, validate , ValidationError

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    nombres = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    apellidos = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    created_at = fields.DateTime(dump_only=True)
    is_active = fields.Bool(missing=True)     

user_schema = UserSchema()
users_schema = UserSchema(many=True)