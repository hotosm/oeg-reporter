from server import ma
from server.models.serializers.utils import CamelCaseSchema


class PlatformSchema(CamelCaseSchema):
    name = ma.Str(required=True)
    url = ma.Url(required=True)


class PlatformListSchema(CamelCaseSchema):
    platform = ma.List(ma.Nested(PlatformSchema), required=False)
