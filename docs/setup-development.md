
## Development setup

#### Configuration

* Copy the example configuration file to start your own configuration: `cp example.env .env`.
* Adjust the `.env` configuration file to fit your configuration.
* Make sure that you followed the setup for the [git repository configuration](/docs/git-repository-setup.md) and the [media wiki configuration](/docs/mediawiki-instance-setup.md) for properly set the variables in the `.env` configuration file. Also, it is necessary to configure the `AUTHORIZATION_TOKEN` environment variable that is used in the requests authorization: 
    - `MEDIAWIKI_BOT_NAME`=bot_name
    - `MEDIAWIKI_BOT_PASSWORD`=bot_password
    - `WIKI_API_ENDPOINT`=https://your-wiki.org/api.php
    - `MYSQL_DATABASE`=my_wiki
    - `MYSQL_USER`=wikiuser
    - `MYSQL_PASSWORD`=example
    - `MYSQL_RANDOM_ROOT_PASSWORD`='yes'
    - `REPORT_FILE_DIR`=report_files_repository
    - `GIT_SSH_PRIVATE_KEY`="your_private_key"
    - `GIT_USER_NAME`=git_user_name
    - `GIT_USER_EMAIL`=git_user_email
    - `AUTHORIZATION_TOKEN`=supersecrettoken

#### Build

##### Build with local python

* Create a Python Virtual Environment, using Python 3.7+:
    * ```python3 -m venv ./venv```
* Activate your virtual environment and install dependencies:
    * Linux/Mac:
        * ```. ./venv/bin/activate```
        * ```pip install -r requirements.txt```
* With your virtual environment activaded, execute the following command for running the server
    * ```py
      python runserver -d
      ```

##### Build with docker

* To have your local environment working using docker it's required that you have [Docker](https://docs.docker.com/get-started/) and [Docker Compose](https://docs.docker.com/compose/) to be installed in your computer. Afterwards you'll just need:
    * One command to get everything together and start the OEG Reporter: `docker-compose up -d backend`
    * After this you are able to report data to a mediawiki instance and to a git repository. Which is described with more details in the [Reporting data section](####reporting-data)

#### Running tests

* For running the tests and see the test coverage run the command from the root of the project
    * ```
      coverage run --source=server -m unittest discover -s server/tests/
      ```
* For generate a html report with the test coverage run the command from the root of the project. After running this command a folder named htmlcov with the report will be generated in the root of the project
    * ```
      coverage html
      ```

#### Reporting data

##### Report to a mediawiki instance

* To add new data to a mediawiki instance, you can send a `POST` request in the endpoint `/wiki/` with a JSON in the following format:

```json
{
    "project":{
        "projectId":1,
        "status":"project status",
        "name":"project name",
        "shortDescription":"short description example",
        "changesetComment":"#project-1",
        "created":"2019-04-08T10:54:25.449637Z",
        "author":"project author",
        "url":"https://tasks.hotosm.org/projects/1",
        "externalSource":{
            "imagery":"imagery url",
            "license":"license description",
            "instructions":"instructions example",
            "perTaskInstructions":"per task instructions"
        },
        "users":[
            {
                "userId":1,
                "userName":"user example"
            
                    }
        ]
    },
    "organisation":{
        "name":"organisation name",
        "url":"http://www.example.com",
        "description":"organisation description"
    },
    "platform":{
        "name":"Platform example",
        "url":"https://tasks.hotosm.org"
    }
}
```

* If everything worked it should create three pages:
    - Overview page - `http://localhost:8080/index.php/Organised_Editing/Activities/Auto_report`
    - Organisation page - `http://localhost:8080/index.php/Organised_Editing/Activities/Auto_report/Organisation_name`
    - Project page - `http://localhost:8080/index.php/Organised_Editing/Activities/Auto_report/Projects/Project_name`

* To update data in the mediawiki instance, you need to send a `PATCH` request in the `/wiki/<organisation_name>/<project_name>` endpoint with the same JSON fields. **Important**: It's not required to send all fields in the JSON because all of them are optional.
* For example, to update some data from the project `Project name` from the organisation `Organisation name` the `PATCH` request will be `http://localhost:5001/wiki/organisation name/project name/` and the JSON data *must* contain at least one field of the shown in the `POST` request previously. In this example the project will have its license and status updated:
```json
{
    "project":{
        "status":"updated project status",
        "name":"updated project name"
    }
}
```


##### Report to a git repository

* To add new data to a git repository, you can send a `POST` request in the endpoint `/git/` with a JSON in the following format:

```json
{
    "project":{
        "projectId":1,
        "status":"project status",
        "name":"project name",
        "shortDescription":"short description example",
        "changesetComment":"#project-1",
        "created":"2019-04-08T10:54:25.449637Z",
        "author":"project author",
        "url":"https://tasks.hotosm.org/projects/1",
        "externalSource":{
            "imagery":"imagery url",
            "license":"license description",
            "instructions":"instructions example",
            "perTaskInstructions":"per task instructions"
        },
        "users":[
            {
                "userId":1,
                "userName":"user example"
            
                    }
        ]
    },
    "organisation":{
        "name":"organisation name",
        "url":"http://www.example.com",
        "description":"organisation description"
    },
    "platform":{
        "name":"Platform example",
        "url":"https://tasks.hotosm.org"
    }
}
```

* If everything worked it should create a file in the git repository cloned in your local computer as described in the [git repository setup](/docs/git-repository-setup.md), commit and push it to the remote repository. The project is reported following this predefined folder structure `github_files/<platform_name>/<organisation_name>`, in this case the structure of the reported project data would be `github_files/Platform_example/organisation_name/project_1.yaml`.

* To update data in the mediawiki instance, you need to send a `PATCH` request in the `/git/<platform_name>/<organisation_name>/<project_id>` endpoint with the same JSON fields. **Important**: It's not required to send all fields in the JSON because all of them are optional.
* For example, to update some data from the project `Project name` from the organisation `Organisation name` the `PATCH` request will be `http://localhost:5001/git/Platform example/organisation name/1/` and the JSON data *must* contain at least one field of the shown in the `POST` request previously. In this example the project will have its license and short description updated:
```json
{
    "project":{
        "shortDescription": "updated short description",
        "externalSource":{
            "license":"updated license",
        }
    }
}
```