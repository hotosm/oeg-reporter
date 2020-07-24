## Git Repository setup

### Configuration

For report data to a git repository it is necessary to have the repository cloned locally. For this you need to run the following commands:
- `git submodule add git@github.com:hotosm/oeg-reporter.git folder_name/` **Important:** The repository clone URL must use SSH password instead HTTPS, otherwise the API will wait for an input for the git username and password
- git submodule init

Afterwards, you need to update the `.env` configuration file with the repository folder name:
- `REPORT_FILE_REPOSITORY_DIR=`folder_name

