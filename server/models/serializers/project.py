from server import ma
from server.models.serializers.utils import CamelCaseSchema


class UserSchema(CamelCaseSchema):
    user_id = ma.Int(required=True)
    user_name = ma.Str(required=True)


class ExternalSourceSchema(CamelCaseSchema):
    imagery = ma.Str(required=True)
    license = ma.Str(required=True)
    instructions = ma.Str(required=True)
    per_task_instructions = ma.Str(required=True)


class ProjectSchema(CamelCaseSchema):
    project_id = ma.Int(required=True)
    status = ma.Str(required=True)
    name = ma.Str(required=True)
    short_description = ma.Str(required=True)
    changeset_comment = ma.Str(required=True)
    author = ma.Str(required=True)
    url = ma.Url(required=True)
    created = ma.DateTime("%Y-%m-%dT%H:%M:%S.%fZ", required=True)
    external_source = ma.Nested(ExternalSourceSchema)
    users = ma.List(ma.Nested(UserSchema))
