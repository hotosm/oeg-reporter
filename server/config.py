import os

from dotenv import load_dotenv


class EnvironmentConfig:

    # Load configuration from file
    load_dotenv(os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".env")))

    REPORT_FILE_DIR = os.path.normpath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            f"{os.getenv('REPORT_FILE_DIR')}/",
        )
    )
