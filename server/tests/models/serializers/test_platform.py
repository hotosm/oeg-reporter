from server.tests.base_test_config import BaseTestCase
from server.models.serializers.platform import PlatformSchema, PlatformListSchema
from marshmallow.exceptions import ValidationError


class TestPlatformSchema(BaseTestCase):
    def setUp(self):
        self.platform_schema = PlatformSchema()
        self.platform_data = {
            "name": "HOT tasking manager",
            "url": "http://www.tasks.hotosm.org/",
        }
        self.platform_list_schema = PlatformListSchema()
        self.platform_list_data = {"platform": [self.platform_data]}

    def test_valid_platform_serialization(self):
        serialized_platform = self.platform_schema.load(self.platform_data)
        platform_fields = self.platform_schema.fields.keys()
        self.assertEqual(serialized_platform.keys(), platform_fields)

    def test_invalid_platform_value_serialization(self):
        self.platform_data["invalid_key"] = "invalid value"
        with self.assertRaises(ValidationError):
            self.platform_schema.load(self.platform_data)

    def test_valid_platform_list_serialization(self):
        serialized_platform_list = self.platform_list_schema.load(
            self.platform_list_data
        )
        self.assertIn(self.platform_data, serialized_platform_list["platform"])
        self.assertCountEqual(
            self.platform_list_data["platform"], serialized_platform_list["platform"]
        )
