from server.tests.base_test_config import BaseTestCase
from server.models.serializers.document import DocumentSchema
from marshmallow.exceptions import ValidationError
from datetime import datetime


class TestDocumentSchema(BaseTestCase):
    def setUp(self):
        self.document_schema = DocumentSchema()
        self.document_data = {
            "project": {
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
            },
            "organisation": {
                "name": "HOT",
                "url": "http://www.hotosm.org/",
                "description": "HOT is an international "
                "team dedicated to humanitarian "
                "action and community development "
                "through open mapping.",
            },
            "platform": {
                "name": "HOT tasking manager",
                "url": "http://www.tasks.hotosm.org/",
            },
        }

    def test_valid_document_serialization(self):
        serialized_document = self.document_schema.load(self.document_data)
        document_fields = self.document_schema.fields.keys()
        self.assertEqual(serialized_document.keys(), document_fields)

    def test_invalid_document_value_serialization(self):
        self.document_data["invalid_key"] = "invalid value"
        with self.assertRaises(ValidationError):
            self.document_schema.load(self.document_data)
