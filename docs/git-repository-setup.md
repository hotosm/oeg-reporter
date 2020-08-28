## Git Repository setup

### Configuration

#### Add repository to local environment
For report data to a git repository it is necessary to have the repository cloned locally. For this you need to run the following commands:
- Add the submodule with the command `git submodule add git@github.com:hotosm/repo-for-storing-reported-files.git folder_name/` 

**Important:** The repository clone URL __must__ use SSH password instead HTTPS, otherwise the API will wait for an input for the git username and password. For this you need to add a SSH key to your hosting service for Git repositories. 

#### Configuring SSH Keys

- Firstly, generate a new SSH key in your local environment with the comand `$ ssh-keygen -t rsa -b 4096 -C "your_email@example.com"`. _If you already have generated a SSH key you can skip to the next step_.
- Then it's necessary add your SSH key to the ssh-agent with the commands `eval "$(ssh-agent -s)"` and `ssh-add ~/.ssh/id_rsa`, that starts the ssh-agent in the background and add your SSH private key to the ssh-agent respectively.
- Finally, add the SSH key to your hosting service for Git repositories. In case you are using GitHub this can be done following the next steps ([from the GitHub docs](https://docs.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account)):
    - In the upper-right corner of any page, click your profile photo, then click Settings.
    - In the user settings sidebar, click SSH and GPG keys. 
    - Click New SSH key or Add SSH key. 
    - Paste your key into the "Key" field. 
- Initialize the submodules with the command `git submodule init`

Afterwards, you need to update the `.env` configuration file with the repository folder name:
- `REPORT_FILE_DIR=`folder_name

If you are going to use docker it's important to set this environment variables in the `.env`:
- `GIT_SSH_PRIVATE_KEY=`your_private_key
- `GIT_USER_NAME=`git_user_name_that_will_create_and_update_files
- `GIT_USER_EMAIL=`git_user_email_that_will_create_and_update_files