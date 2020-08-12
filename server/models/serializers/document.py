from server import ma
from server.models.serializers.utils import CamelCaseSchema
from server.models.serializers.organisation import OrganisationSchema
from server.models.serializers.platform import PlatformSchema
from server.models.serializers.project import ProjectSchema


class DocumentSchema(CamelCaseSchema):
    project = ma.Nested(ProjectSchema)
    organisation = ma.Nested(OrganisationSchema)
    platform = ma.Nested(PlatformSchema)


class OrganisationPageSchema(CamelCaseSchema):
    project = ma.List(ma.Nested(ProjectSchema))
    organisation = ma.Nested(OrganisationSchema)
    platform = ma.Nested(PlatformSchema)


class OverviewPageSchema(CamelCaseSchema):
    organisation = ma.List(ma.Nested(OrganisationSchema))
    platform = ma.List(ma.Nested(PlatformSchema))
