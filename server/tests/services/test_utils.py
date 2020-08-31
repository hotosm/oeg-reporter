import copy

from server.tests.base_test_config import BaseTestCase
from server.tests.helpers import utils
from server.services.utils import update_document


class TestServiceUtils(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.document_data = utils.document_data

    def test_update_document_key(self):
        update_fields = {"project": {"name": "update project name"}}
        updated_document = update_document(self.document_data, update_fields)

        expected_document = copy.deepcopy(self.document_data)
        expected_document["project"]["name"] = "update project name"

        self.assertDictEqual(expected_document, updated_document)

    def test_update_document_nested_key(self):
        update_fields = {"project": {"externalSource": {"license": "updated license"}}}
        updated_document = update_document(self.document_data, update_fields)

        expected_document = copy.deepcopy(self.document_data)
        expected_document["project"]["externalSource"]["license"] = "updated license"

        self.assertDictEqual(expected_document, updated_document)

    def test_update_document_list_key(self):
        updated_users_list = [
            {"userName": "user name example", "userId": 1},
            {"userName": "second user name example", "userId": 2},
        ]
        update_fields = {"project": {"users": updated_users_list}}
        updated_document = update_document(self.document_data, update_fields)

        expected_document = copy.deepcopy(self.document_data)
        expected_document["project"]["users"] = updated_users_list

        self.assertDictEqual(expected_document, updated_document)
