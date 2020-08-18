import os

from dotenv import load_dotenv


class EnvironmentConfig:

    # Load configuration from file
    load_dotenv(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".env")))

    REPORT_FILE_DIR = os.path.normpath(
        os.path.join(
            os.path.dirname(__file__), "..", f"{os.getenv('REPORT_FILE_DIR')}/",
        )
    )
    WIKI_API_ENDPOINT = os.getenv("WIKI_API_ENDPOINT")
    MEDIAWIKI_BOT_NAME = os.getenv("MEDIAWIKI_BOT_NAME")
    MEDIAWIKI_BOT_PASSWORD = os.getenv("MEDIAWIKI_BOT_PASSWORD")
