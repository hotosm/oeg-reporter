import yaml
import os


class FileService:
    @staticmethod
    def create_file(file_content: str, file_path: str, filename: str) -> None:
        """
        Create a file

        Keyword arguments:
        file_content -- The contents of the updated file
        file_path -- The directory of the file
        filename -- The name of the file

        Raises:
        ValueError -- Raised when the file already exists
        """
        try:
            if not os.path.exists(file_path):
                os.makedirs(file_path)
            f = open(f"{file_path}/{filename}", "x")
            f.write(file_content)
            f.close()
        except FileExistsError:
            raise ValueError(
                f"Unable to write {filename} in {file_path}. File already exists"
            )

    def update_file(file_content: str, file_path: str, filename: str) -> None:
        """
        Update an existing file

        Keyword arguments:
        file_content -- The contents of the updated file
        file_path -- The directory of the file
        filename -- The name of the file

        Raises:
        ValueError -- Raised when the file doesn't exists
        """
        try:
            f = open(f"{file_path}/{filename}", "w+")
            f.write(file_content)
            f.close()
        except FileNotFoundError:
            raise ValueError(f"Unable to open {filename} located in {file_path}")

    @staticmethod
    def get_content(file_path):
        """
        Get the content of a file and returns it as string

        Keyword arguments:
        file_path -- The directory of the file

        Raises:
        ValueError -- Raised when the file doesn't exists

        Returns:
        file_content -- The content of the file as string
        """
        try:
            f = open(file_path, "r")
            file_content = f.read()
            f.close()
            return file_content
        except FileNotFoundError:
            raise ValueError(f"Unable to open file located in {file_path}")

    @staticmethod
    def dict_to_yaml(yaml_dict: dict) -> str:
        """
        Parse a YAML dictionary to a string

        Keyword arguments:
        yaml_dict -- The dictionary representation of a YAML

        Returns:
        yaml_str -- The string representation of a YAML
        """
        yaml_str = yaml.dump(yaml_dict, allow_unicode=True)
        return yaml_str

    @staticmethod
    def yaml_to_dict(yaml_str: str) -> dict:
        """
        Parse a YAML string to a dictionary

        Keyword arguments:
        yaml_str -- The string representation of a YAML

        Returns:
        yaml_dict -- The dictionary representation of a YAML
        """
        yaml_dict = yaml.load(yaml_str, Loader=yaml.FullLoader)
        return yaml_dict
