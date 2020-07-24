from os import listdir
from os.path import isfile, join
import shutil

from flask import current_app

import git

from server.services.git.file_service import FileService
from server.models.serializers.document import DocumentSchema


class GitService:
    def __init__(self, platfotm_name, organisation_name, project_id):
        self.yaml_file_dir = "github_files"
        self.platform_name = platfotm_name.replace(" ", "_")
        self.organisation_name = organisation_name.replace(" ", "_")
        self.project_id = project_id
        self.repo = git.Repo(current_app.config["REPORT_FILE_REPOSITORY_DIR"])
        self.document_dir = (
            f'{current_app.config["REPORT_FILE_REPOSITORY_DIR"]}/'
            f"{self.yaml_file_dir}/"
            f"{self.platform_name}/"
            f"{self.organisation_name}"
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
        yaml_file = FileService.dict_to_yaml(DocumentSchema().dump(obj=document))
        filename = "project_" + str(self.project_id) + ".yaml"
        FileService.create_file(yaml_file, self.document_dir, filename)

        # push the file  to the remote repo
        self.repo.git.add([f"{self.document_dir}/{filename}"])
        commit_message = f"Add project {str(self.project_id)}"
        self.commit_file(commit_message)

    def update_document(self, update_document: dict) -> dict:
        """
        Update a document in a git repository

        Keyword arguments:
        update_document -- The content of document being updated
        """
        # Write changes of the file in the local repo
        filename = "project_" + str(self.project_id) + ".yaml"
        yaml_file = FileService.get_content(f"{self.document_dir}/{filename}")
        update_yaml_file = self.update_yaml_file(update_document, yaml_file)
        FileService.update_file(update_yaml_file, self.document_dir, filename)

        # if the platform/org name is updated it's necessary change
        # the directory structure of the repository
        if self.is_platform_or_org_name_being_updated(update_document):
            # Update the directory structure of the repo
            update_dir = self.get_platform_and_org_name_updated_dir(update_document)
            document_dir_files, update_document_dir_files = self.get_staged_files(
                update_dir
            )
            shutil.move(self.document_dir, update_dir)

            # Stage files
            self.repo.git.add(update_document_dir_files)
            self.repo.git.rm(document_dir_files)
        else:
            self.repo.git.add([f"{self.document_dir}/{filename}"])

        # push changes to the remote repo
        commit_message = f"Update project {str(self.project_id)}"
        self.commit_file(commit_message)

    def is_platform_or_org_name_being_updated(self, update_document: dict) -> bool:
        """
        Check if an org or platform name is being updated

        Keyword arguments:
        update_document -- The content of document being updated

        Returns:
        bool -- Boolean indicating if a org or platform name is being updated
        """
        if (
            "organisation" in update_document.keys()
            and "name" in update_document["organisation"]
            or "platform" in update_document.keys()
            and "name" in update_document["platform"]
        ):
            return True
        else:
            return False

    def get_staged_files(self, update_dir: str) -> tuple:
        """
        Get all files that need to be staged when an org/platform
        name is updated

        Keyword arguments:
        update_dir -- The updated directory where files are
                      going to be stored

        Returns:
        tuple -- Tuple with two lists containing all files that need
                 to be staged
        """
        document_dir_files = [
            f"{self.document_dir}/{dir_file}"
            for dir_file in listdir(f"{self.document_dir}/")
            if isfile(join(f"{self.document_dir}/", dir_file))
        ]
        update_document_dir_files = [
            dir_file.replace(f"{self.document_dir}", f"{update_dir}")
            for dir_file in document_dir_files
        ]
        return document_dir_files, update_document_dir_files

    def get_platform_and_org_name_updated_dir(self, update_document: dict) -> str:
        """
        Generate updated directory with updated organisation / platform names

        Keyword arguments:
        update_document -- The content of document being updated

        Returns:
        update_dir -- The updated directory with updated
                      organisation / platform names
        """
        if (
            "organisation" in update_document.keys()
            and "name" in update_document["organisation"]
            and "platform" in update_document.keys()
            and "name" in update_document["platform"]
        ):
            platform_name = update_document["platform"]["name"].replace(" ", "_")
            organisation_name = update_document["organisation"]["name"].replace(
                " ", "_"
            )

            update_dir = (
                f"{current_app.config['REPORT_FILE_REPOSITORY_DIR']}/"
                f"{self.yaml_file_dir}/{platform_name}"
                f"/{organisation_name}"
            )

        elif (
            "organisation" in update_document.keys()
            and "name" in update_document["organisation"]
            and "platform" not in update_document.keys()
        ):
            organisation_name = update_document["organisation"]["name"].replace(
                " ", "_"
            )
            update_dir = (
                f"{current_app.config['REPORT_FILE_REPOSITORY_DIR']}/"
                f"{self.yaml_file_dir}/{self.platform_name}/"
                f"{organisation_name}"
            )

        elif (
            "organisation" not in update_document.keys()
            and "platform" in update_document.keys()
            and "name" in update_document["platform"]
        ):
            platform_name = update_document["platform"]["name"].replace(" ", "_")
            update_dir = (
                f"{current_app.config['REPORT_FILE_REPOSITORY_DIR']}/"
                f"{self.yaml_file_dir}/{platform_name}/"
                f"{self.organisation_name}"
            )
        return update_dir

    def update_yaml_file(self, update_document: dict, yaml_str: str) -> str:
        """
        Generate the request data for update a file in a git repository

        Keyword arguments:
        update_document -- The content of document being updated
        yaml_str -- The string of the yaml present in the git repository that
                    is being updated

        Returns:
        update_yaml_file -- The request data for update a file
                         in a github repository
        """
        update_yaml_dict = DocumentSchema(partial=True).load(
            data=FileService.yaml_to_dict(yaml_str)
        )
        update_fields = DocumentSchema(partial=True).load(data=update_document)

        # Update yaml dictionary with new values
        for key in update_fields.keys():
            for nested_key, value in update_fields[key].items():
                if isinstance(update_fields[key][nested_key], list):
                    update_yaml_dict[key][nested_key] = list(value)
                elif isinstance(update_fields[key][nested_key], dict):
                    for nested_dict_key in update_fields[key][nested_key]:
                        update_yaml_dict[key][nested_key][
                            nested_dict_key
                        ] = update_fields[key][nested_key][nested_dict_key]
                else:
                    update_yaml_dict[key][nested_key] = value

        # Parse the updated yaml dictionary into yaml
        update_yaml_file = FileService.dict_to_yaml(
            DocumentSchema().dump(obj=update_yaml_dict)
        )
        return update_yaml_file
