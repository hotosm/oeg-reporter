## Mediawiki instance setup

For report data to a mediawiki instance it is necessary to have a local mediawiki instance, The following describes how to do all the configuration of a mediawiki.

### Build database

The mediawiki instance requires a database like MySQL, MariaDB or equivalent. Here it's used a MariaDB and for configuring the database is very simple. Update the `.env` configuration file with the following variables:
- `MYSQL_DATABASE`=my_wiki
- `MYSQL_USER`=wikiuser
- `MYSQL_PASSWORD`=example
- `MYSQL_RANDOM_ROOT_PASSWORD`='yes'

With the configuration file updated run the command `docker-compose up -d database`  to get a working MariaDB instance.

### Build MediaWiki

For running a local mediawiki instance you should install [Docker](https://docs.docker.com/get-started/) and [Docker Compose](https://docs.docker.com/compose/). Afterwards you'll just need run the command `docker-compose up -d` and configure the mediawiki in your browser at `http://127.0.0.1:8080`. In case you face some difficults configuring the mediawiki database connection, just add the docker-compose service name `database` as the database host.<br>
Once you finish the configuration you'll be prompt to download a file named `LocalSettings.php`, just confirm the download of this file and place it in the root of the project.
* In order to get the mediawiki instance working, you have to uncomment this line  of the `docker-compose.yml`
    - `# - ./LocalSettings.php:/var/www/html/LocalSettings.php`
* And rebuild the docker container with the newly configured mediawiki instance with the following commands:
    - docker-compose stop mediawiki
    - docker-compose up --build mediawiki

### Creating a bot

For creating a bot visit your browser at `http://127.0.0.1:8080/index.php/Special:BotPasswords` and login with the root user created during the mediawiki configuration. Finally, you just have to create your bot with the name you want and it will generate a password for it.

#### Configuring Environment variables

For get everything working properly with the API you need to update the `.env` configuration file with the mediawiki information collected during the previous steps:
- `MEDIAWIKI_BOT_NAME`=bot_name
- `MEDIAWIKI_BOT_PASSWORD`=bot_password
- `WIKI_API_ENDPOINT`=https://127.0.0.1:8080/api.php