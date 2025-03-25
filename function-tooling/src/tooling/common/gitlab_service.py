from typing import Callable

import gitlab
from gitlab.v4.objects import ProjectMergeRequest
from pylibraryaws.secrets_manager import SecretsManager


class GitLabService:
    __GITLAB_BASE_URL = "https://natwest.gitlab-dedicated.com/"
    __GITLAB_SECRET_NAME = "gitlab-tooling/1"  # nosec

    def __init__(self, secrets_manager: SecretsManager) -> None:
        self.__secrets_manager: SecretsManager = secrets_manager
        self.__scm_private_token = self.__get_scm_private_token()

    def get_merge_request(self, merge_request_url: str) -> ProjectMergeRequest:
        gitlab_client = gitlab.Gitlab(url=GitLabService.__GITLAB_BASE_URL,
                                      private_token=self.__scm_private_token())

        project_path = merge_request_url.split(GitLabService.__GITLAB_BASE_URL)[1].split("/-/merge_requests/")[0]
        project = gitlab_client.projects.get(project_path)

        merge_request_id = merge_request_url.split("/-/merge_requests/")[1]
        return project.mergerequests.get(merge_request_id)

    def __get_scm_private_token(self) -> Callable[[], str]:
        token: str = self.__secrets_manager.get_secret_value(GitLabService.__GITLAB_SECRET_NAME).get("token")
        return lambda: token
