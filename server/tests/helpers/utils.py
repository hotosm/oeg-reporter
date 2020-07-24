from datetime import datetime

from server.services.git.file_service import FileService


document_data = {
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
    "platform": {"name": "HOT tasking manager", "url": "http://www.tasks.hotosm.org/"},
}

document_yaml = FileService.dict_to_yaml(document_data)
