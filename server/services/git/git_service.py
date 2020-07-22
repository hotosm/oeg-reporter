from flask import current_app


from server.services.git.file_service import FileService
import git


class GitService:
    def __init__(self, platfotm_name, organisation_name, project_id):
        self.file_folder = "github_files"
        self.platform_name = platfotm_name.replace(" ", "_")
        self.organisation_name = organisation_name.replace(" ", "_")
        self.project_id = project_id
        self.repo = git.Repo(current_app.config["REPORT_FILE_REPOSITORY_PATH"])
        self.file_path = f"{self.platform_name}/" f"{self.organisation_name}"
        self.document_folder = (
            f'{current_app.config["REPORT_FILE_REPOSITORY_PATH"]}/'
            f"{self.file_folder}/"
            f"{self.file_path}"
        )

    def commit_file(self, commit_message: str) -> None:
        """
        Commit changes in the local git repository and push
        it to the remote repo

        Keyword arguments:
        commit_message -- The message of the commit
        """
        self.repo.index.commit(commit_message)
        origin = self.repo.remote(name="origin")
        origin.push()

    def create_document(self, document: dict) -> None:
        """
        Create a new file in a git repository

        Keyword arguments:
        document -- The string of the yaml file being created
        """
        # Parse dict to yaml and write it to the local repo
        yaml_file = FileService.dict_to_yaml(document)
        filename = "project_" + str(self.project_id) + ".yaml"
        FileService.create_file(yaml_file, self.document_folder, filename)

        # push the file  to the remote repo
        self.repo.git.add([f"{self.document_folder}/{filename}"])
        commit_message = f"Add project {str(self.project_id)}"
        self.commit_file(commit_message)
