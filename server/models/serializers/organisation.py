from server import ma
from server.models.serializers.utils import CamelCaseSchema


class OrganisationSchema(CamelCaseSchema):
    description = ma.Str(required=True)
    url = ma.Url(required=True)
    name = ma.Str(required=True)


class OrganisationListSchema(CamelCaseSchema):
    organisation = ma.List(ma.Nested(OrganisationSchema))
