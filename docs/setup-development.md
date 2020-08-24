
## Development setup

#### Configuration

* Copy the example configuration file to start your own configuration: `cp example.env .env`.
* Adjust the `.env` configuration file to fit your configuration.
* Make sure that you followed the setup for the [git repository configuration](/docs/git-repository-setup.md) and the [media wiki configuration](/docs/mediawiki-instance-setup.md) for properly set the variables in the `.env` configuration file:
    - `REPORT_FILE_DIR`=report_files_repository
    - `MEDIAWIKI_BOT_NAME`=bot_name
    - `MEDIAWIKI_BOT_PASSWORD`=bot_password
    - `WIKI_API_ENDPOINT`=https://your-wiki.org/api.php
    - `MYSQL_DATABASE`=my_wiki
    - `MYSQL_USER`=wikiuser
    - `MYSQL_PASSWORD`=example
    - `MYSQL_RANDOM_ROOT_PASSWORD`='yes'

#### Build

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

## Running tests

* For running the tests and see the test coverage run the command from the root of the project
    * ```
      coverage run --source=server -m unittest discover -s server/tests/
      ```
* For generate a html report with the test coverage run the command from the root of the project. After running this command a folder named htmlcov with the report will be generated in the root of the project
    * ```
      coverage html
      ```