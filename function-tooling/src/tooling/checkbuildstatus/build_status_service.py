from typing import Any
from typing import Callable, cast

from gitlab.v4.objects import ProjectMergeRequestPipeline
from pylibraryaws.secrets_manager import SecretsManager

from tooling.common.gitlab_service import GitLabService


class BuildStatusService:
    __GITLAB_BASE_URL = "https://natwest.gitlab-dedicated.com/"
    __GITLAB_SECRET_NAME = "gitlab-tooling/1"  # nosec

    def __init__(self, secrets_manager: SecretsManager, gitlab_service: GitLabService) -> None:
        self.__secrets_manager: SecretsManager = secrets_manager
        self.__scm_private_token = self.__get_scm_private_token()
        self.__gitlab_service = gitlab_service

    def fetch_build_status(self, merge_request_url: str) -> dict[str, Any]:
        pipelines = self.__get_merge_request_pipelines_status(merge_request_url)

        if not pipelines:
            return {
                "statusCode": 200,
                "body": "build has not started yet"
            }

        pipeline_status = pipelines[0].status
        return {
            "statusCode": 200,
            "body": f'{pipeline_status}'
        }

    def __get_scm_private_token(self) -> Callable[[], str]:
        token: str = self.__secrets_manager.get_secret_value(BuildStatusService.__GITLAB_SECRET_NAME).get("token")
        return lambda: token

    def __get_merge_request_pipelines_status(self, merge_request_url: str) -> list[ProjectMergeRequestPipeline]:
        merge_request = self.__gitlab_service.get_merge_request(merge_request_url)
        return cast(list[ProjectMergeRequestPipeline], merge_request.pipelines.list())
