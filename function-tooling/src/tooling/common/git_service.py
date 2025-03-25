from os import path
from typing import Callable

import dulwich.porcelain as porcelain
import requests
from dulwich.repo import Repo
from pylibraryaws.secrets_manager import SecretsManager
from pylibrarycore.exceptions.exceptions import InternalServerError, BadRequestException
from pylibrarycore.logging.logger_utils import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


class GitService:
    __GITLAB_URL = ("https://natwest.gitlab-dedicated.com/natwestgroup/DigitalX/RetailBankingDigiTech/DigitalChannels"
                    "/DigiBankingMplatform/{}")
    __GITLAB_SECRET_NAME = "gitlab-tooling/1"  # nosec

    def __init__(self, secrets_manager: SecretsManager) -> None:
        self.__secrets_manager: SecretsManager = secrets_manager
        self.__scm_private_token = self.__get_scm_private_token()

    def clone_checkout(self, repo_name: str, local_dir: str, branch: str | None = "develop") -> Repo:
        repo_url: str = GitService.__GITLAB_URL.format(repo_name)
        repo: Repo = porcelain.clone(
            repo_url,
            username="_",
            password=self.__scm_private_token(),
            target=path.join(local_dir, repo_name),
            checkout=True
        )
        logger.info("Cloned %s to %s", repo_name, path.join(local_dir, repo_name))

        try:
            porcelain.checkout_branch(repo, f'origin/{branch}')
        except KeyError as e:
            error_message: str = f'Unable to checkout {branch}'
            logger.error(error_message)
            raise BadRequestException(error_message, e)

        logger.info("%s checked out", branch)
        return repo

    @staticmethod
    def commit(repo: Repo, jira_number: str, msg: str) -> None:
        for unstaged in porcelain.status(repo).unstaged:  # type: ignore
            porcelain.add(repo, path.join(repo.path, unstaged.decode('UTF-8')))  # type: ignore
            logger.info("Adding file: [%s]", path.join(repo.path, unstaged.decode('UTF-8')))
        porcelain.commit(repo, f'{jira_number}: {msg}')  # type: ignore

    def push(self, repo: Repo, repo_name: str) -> None:
        active_branch = porcelain.active_branch(repo).decode('UTF-8')  # type: ignore
        repo_url = GitService.__GITLAB_URL.format(repo_name)
        remote_ref = f'refs/heads/{active_branch}'
        porcelain.push(
            repo,
            username='_',
            password=self.__scm_private_token(),
            remote_location=repo_url,
            refspecs=[f'{active_branch}:{remote_ref}']
        )
        logger.info("Changes pushed to branch. Repo: [%s], branch: [%s]", repo_name, active_branch)

    @staticmethod
    def create_new_branch(repo: Repo, branch: str) -> None:
        porcelain.branch_create(repo, branch)
        porcelain.checkout_branch(repo, branch)
        logger.info("Switched to a new branch: [%s]", branch)

    def create_merge_request(self,
                             repo: Repo,
                             repo_name: str,
                             target_branch: str,
                             jira_number: str) -> str:
        gitlab_url = "https://natwest.gitlab-dedicated.com"
        project_path = (f'natwestgroup%2FDigitalX%2FRetailBankingDigiTech%2FDigitalChannels%2FDigiBankingMplatform%2F'
                        f'{repo_name}')
        url = f"{gitlab_url}/api/v4/projects/{project_path}/merge_requests"
        active_branch = porcelain.active_branch(repo).decode("UTF-8")  # type: ignore
        mr_data = {
            "source_branch": active_branch,
            "target_branch": target_branch,
            "title": f'{jira_number}: Updating project dependencies'
        }
        headers = {
            "Authorization": f'Bearer {self.__scm_private_token()}'
        }
        response = requests.post(url, headers=headers, data=mr_data, timeout=20)
        if response.status_code == 201:
            return str(response.json()['web_url'])
        else:
            raise InternalServerError(f'Failed to create merge request: {response.status_code}')

    def __get_scm_private_token(self) -> Callable[[], str]:
        token: str = self.__secrets_manager.get_secret_value(GitService.__GITLAB_SECRET_NAME).get("token")
        return lambda: token
