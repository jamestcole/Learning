import tempfile
from os import path

from tooling.common.git_service import GitService
from tooling.setversion.pom_update_service import PomUpdateService


class SetVersionService:

    def __init__(self, git_service: GitService, pom_updater_service: PomUpdateService) -> None:
        self.__git_service = git_service
        self.__pom_update_service = pom_updater_service

    def set_version(self, repo_name: str,
                    new_pom_version: str,
                    jira_number: str,
                    branch: str) -> None:
        with tempfile.TemporaryDirectory() as local_dir:
            repo = self.__git_service.clone_checkout(repo_name, local_dir, branch)
            self.__pom_update_service.update_pom_versions(path.join(local_dir, repo_name), new_pom_version)
            self.__git_service.commit(repo, jira_number, f'updating pom version to {new_pom_version}')
            self.__git_service.push(repo, repo_name)
