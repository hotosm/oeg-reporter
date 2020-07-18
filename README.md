# OEG Reporter

Repository for report content from Tasking Manager to OpenStreetMap 

## Build

### Python dependencies

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

* For running the tests and see the test coverage run the command
    * ```
      coverage run --source=server -m unittest discover -s server/tests/
      ```
* For generate a html report with the test coverage run the command. After running this command a folder named htmlcov with the report will be generated in the root of the project
    * ```
      coverage html
      ```