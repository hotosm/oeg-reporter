from marshmallow.exceptions import ValidationError

from server.tests.base_test_config import BaseTestCase
from server.models.serializers.organisation import (
    OrganisationSchema,
    OrganisationListSchema,
)


class TestOrganisationSchema(BaseTestCase):
    def setUp(self):
        self.organisation_schema = OrganisationSchema()
        self.organisation_data = {
            "name": "HOT",
            "url": "http://www.hotosm.org/",
            "description": "HOT is an international "
            "team dedicated to humanitarian "
            "action and community development "
            "through open mapping.",
        }
        self.organisation_list_schema = OrganisationListSchema()
        self.organisation_list_data = {"organisation": [self.organisation_data]}

    def test_valid_organisation_serialization(self):
        serialized_organisation = self.organisation_schema.load(self.organisation_data)
        organisation_fields = self.organisation_schema.fields.keys()
        self.assertEqual(serialized_organisation.keys(), organisation_fields)

    def test_invalid_organisation_value_serialization(self):
        self.organisation_data["invalid_key"] = "invalid value"
        with self.assertRaises(ValidationError):
            self.organisation_schema.load(self.organisation_data)

    def test_valid_organisation_list_serialization(self):
        serialized_organisation_list = self.organisation_list_schema.load(
            self.organisation_list_data
        )
        self.assertIn(
            self.organisation_data, serialized_organisation_list["organisation"]
        )
        self.assertCountEqual(
            self.organisation_list_data["organisation"],
            serialized_organisation_list["organisation"],
        )
