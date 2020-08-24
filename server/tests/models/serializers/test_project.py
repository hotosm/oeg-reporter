from datetime import datetime

from marshmallow.exceptions import ValidationError

from server.tests.base_test_config import BaseTestCase
from server.models.serializers.project import (
    UserSchema,
    ExternalSourceSchema,
    ProjectSchema,
)


class TestUserSchema(BaseTestCase):
    def setUp(self):
        self.user_schema = UserSchema()
        self.user_data = {"userId": 1, "userName": "a mapper"}

    def test_valid_user_serialization(self):
        serialized_user = self.user_schema.load(self.user_data)
        user_fields = self.user_schema.fields.keys()
        self.assertEqual(serialized_user.keys(), user_fields)

    def test_invalid_user_id_serialization(self):
        invalid_id = "1"
        invalid_user_data = dict(self.user_data)
        invalid_user_data["id"] = invalid_id
        with self.assertRaises(ValidationError):
            self.user_schema.load(invalid_user_data)

    def test_invalid_user_value_serialization(self):
        self.user_data["invalid_key"] = "invalid value"
        with self.assertRaises(ValidationError):
            self.user_schema.load(self.user_data)


class TestExternalSourceSchema(BaseTestCase):
    def setUp(self):
        self.external_source_schema = ExternalSourceSchema()
        self.external_source_data = {
            "imagery": "imagery example",
            "license": "license example",
            "instructions": "instructions example",
            "perTaskInstructions": "per task instructions example",
        }

    def test_valid_external_source_serialization(self):
        serialized_external_source = self.external_source_schema.load(
            self.external_source_data
        )
        external_source_fields = self.external_source_schema.fields.keys()
        self.assertEqual(serialized_external_source.keys(), external_source_fields)

    def test_invalid_external_source_id_serialization(self):
        invalid_imagery = 1
        invalid_external_source_data = dict(self.external_source_data)
        invalid_external_source_data["imagery"] = invalid_imagery
        with self.assertRaises(ValidationError):
            self.external_source_schema.load(invalid_external_source_data)

    def test_invalid_external_source_value_serialization(self):
        self.external_source_data["invalid_key"] = "invalid value"
        with self.assertRaises(ValidationError):
            self.external_source_schema.load(self.external_source_data)


class TestProjectSchema(BaseTestCase):
    def setUp(self):
        self.project_schema = ProjectSchema()
        self.project_data = {
            "projectId": 1,
            "status": "status example",
            "name": "project name example",
            "shortDescription": "short description example",
            "changesetComment": "changeset comment example",
            "author": "project author example",
            "url": "http://example.com",
            "created": datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S.%fZ"),
            "externalSource": {
                "imagery": "imagery example",
                "license": "license example",
                "instructions": "instructions example",
                "perTaskInstructions": "per task instructions example",
            },
            "users": [{"userName": "user name example", "userId": 1}],
        }

    def test_valid_project_serialization(self):
        serialized_project = self.project_schema.load(self.project_data)
        project_fields = self.project_schema.fields.keys()
        self.assertEqual(serialized_project.keys(), project_fields)

    def test_invalid_project_value_serialization(self):
        self.project_data["invalid_key"] = "invalid value"
        with self.assertRaises(ValidationError):
            self.project_schema.load(self.project_data)
