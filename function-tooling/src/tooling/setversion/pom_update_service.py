import glob
import os
import xml.etree.ElementTree as ET  # nosec
from xml.etree.ElementTree import ElementTree, Element  # nosec

from packaging import version
from pylibrarycore.logging.logger_utils import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


class PomUpdateService:
    __ns_map = {
        "": "http://maven.apache.org/POM/4.0.0"
    }

    def update_pom_versions(self, repo_root_dir: str, new_pom_version: str) -> None:
        logger.info("Updating pom.xml files under %s to version %s", repo_root_dir, new_pom_version)
        pom_paths = glob.glob(f'{repo_root_dir}/**/*pom.xml')
        pom_paths.insert(0, os.path.join(repo_root_dir, "pom.xml"))

        for p in set(pom_paths):
            self.__update_pom_version(p, new_pom_version)

    @staticmethod
    def __update_pom_version(pom_path: str, new_pom_version: str) -> None:
        ET.register_namespace("", "http://maven.apache.org/POM/4.0.0")  # nosec
        xml_parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))  # nosec
        pom = ET.parse(pom_path, xml_parser)  # nosec
        version_element = PomUpdateService.__get_version_element(pom)
        PomUpdateService.__validate_versions(pom_path, version_element, new_pom_version)
        version_element.text = new_pom_version.__str__()  # type: ignore
        PomUpdateService.__save_updated_pom(pom, pom_path)

    @staticmethod
    def __get_version_element(pom: ElementTree) -> Element | None:
        version_element = pom.find("./version", PomUpdateService.__ns_map)
        if version_element is not None:
            return version_element
        else:
            return pom.find("./parent/version", PomUpdateService.__ns_map)

    @staticmethod
    def __validate_versions(pom_path: str, version_element: Element | None, new_pom_version: str) -> None:
        if version_element is None:
            raise ValueError(f'Could not locate a version element in {pom_path} - cannot update')

        extant_pom_version = version_element.text
        parsed_extant_pom_version = version.parse(extant_pom_version.removesuffix("-SNAPSHOT"))  # type: ignore
        parsed_new_pom_version = version.parse(new_pom_version.removesuffix("-SNAPSHOT"))

        if parsed_extant_pom_version >= parsed_new_pom_version:
            raise ValueError(
                f'New POM version of {new_pom_version} must be > {extant_pom_version} - cannot update')

    @staticmethod
    def __save_updated_pom(pom: ElementTree, pom_path: str) -> None:
        logger.info("Updated %s", pom_path)
        pom.write(f'{pom_path}')  # nosec
