import requests
from typing import Optional
from pylibraryaws.secrets_manager import SecretsManager
from pylibrarycore.exceptions.exceptions import InternalServerError


class NexusService:
    __NEXUS_URL = 'https://nexus.mplatform.co.uk'
    __NEXUS_REPO = 'mob-libs-releases-local'
    __NEXUS_ARTIFACT_GROUP_ID = 'com.rbs.digital.mobile'
    __NEXUS_ARTIFACT_EXTENSION = 'pom'
    __NEXUS_CREDS_SECRET_NAME = "nexus-tooling/1"  # nosec

    def __init__(self, secrets_manager: SecretsManager) -> None:
        self.__secrets_manager: SecretsManager = secrets_manager
        self.__nexus_username, self.__nexus_password = self._get_nexus_creds()

    def fetch_latest_version(self, artifact_id: str) -> Optional[str]:
        response = requests.get(
            self._build_nexus_url(artifact_id),
            auth=(self.__nexus_username, self.__nexus_password),
            timeout=20)

        if response.status_code == 200:
            items = response.json().get('items', [])
            if items:
                return str(items[0].get('version'))
            raise InternalServerError(f'No version has been found for artifact id: [{artifact_id}]')
        else:
            raise InternalServerError(f'Failed to call Nexus. Status code: {response.status_code} '
                                      f'and body: {response.json()}')

    def _build_nexus_url(self, artifact_id: str) -> str:
        return (
            f"{self.__NEXUS_URL}/service/rest/v1/search?"
            f"repository={self.__NEXUS_REPO}&"
            f"maven.groupId={self.__NEXUS_ARTIFACT_GROUP_ID}&"
            f"maven.artifactId={artifact_id}&"
            f"maven.extension={self.__NEXUS_ARTIFACT_EXTENSION}&"
            "sort=version&direction=desc"
        )

    def _get_nexus_creds(self) -> tuple[str, str]:
        nexus_creds = self.__secrets_manager.get_secret_value(NexusService.__NEXUS_CREDS_SECRET_NAME)
        return nexus_creds.get('username'), nexus_creds.get('password')
