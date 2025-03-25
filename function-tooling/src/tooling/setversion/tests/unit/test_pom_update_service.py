import re
from unittest.mock import MagicMock
from xml.etree.ElementTree import ElementTree, XML

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pytest_mock import MockerFixture

from tooling.setversion.pom_update_service import PomUpdateService

mock_top_level_pom = """
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.rbs.digital.mobile</groupId>
        <artifactId>mobile-base-parent</artifactId>
        <version>3.146.0</version>
    </parent>
    <artifactId>mobile-image</artifactId>
    <version>4.11.1-SNAPSHOT</version>
    <packaging>pom</packaging>
</project>"""

mock_child_pom = """
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.rbs.digital.mobile</groupId>
        <artifactId>mobile-image</artifactId>
        <version>4.11.1-SNAPSHOT</version>
    </parent>
    <artifactId>mobile-image-acceptance</artifactId>
    <packaging>jar</packaging>
</project>"""


@pytest.fixture(autouse=True)
def mock_glob(mocker: MockerFixture):
    return mocker.patch("glob.glob")


under_test = PomUpdateService()


def test_given_pom_with_version_should_update(fs: FakeFilesystem, mock_glob: MagicMock):
    # given
    pom_xml_path = "/some/pom-path/pom.xml"
    fs.create_file(pom_xml_path, contents=mock_top_level_pom)
    mock_glob.return_value = [pom_xml_path]
    new_pom_version = "4.11.12"

    # when
    under_test.update_pom_versions("/some/pom-path", new_pom_version)

    # then
    with open(pom_xml_path) as f:
        assert re.match(f'^.*?<version>{new_pom_version}</version>.*?$', f.read(), re.DOTALL)


def test_given_child_pom_should_update_parent(fs: FakeFilesystem, mock_glob: MagicMock):
    # given
    pom_xml_path = "/some/pom-path/pom.xml"
    fs.create_file(pom_xml_path, contents=mock_child_pom)
    mock_glob.return_value = [pom_xml_path]
    new_pom_version = "4.11.12"

    # when
    under_test.update_pom_versions("/some/pom-path", new_pom_version)

    # then
    with open(pom_xml_path) as f:
        assert re.match(f'^.*?<version>{new_pom_version}</version>.*?$', f.read(), re.DOTALL)


def test_given_invalid_pom_xml_should_not_write(mock_glob: MagicMock, mocker: MockerFixture):
    # given
    pom_xml = "some/pom-path/pom.xml"
    mock_glob.return_value = [pom_xml]
    mocker.patch("xml.etree.ElementTree.parse").return_value = ElementTree(XML("<invalid/>"))
    mock_et_write = mocker.patch("xml.etree.ElementTree.ElementTree.write")

    # when
    with pytest.raises(ValueError, match=f'Could not locate a version element in {pom_xml} - cannot update'):
        under_test.update_pom_versions("some/pom-path/", "123.45.6")

    # then
    mock_et_write.assert_not_called()


def test_given_older_pom_version_should_not_write(mock_glob: MagicMock, mocker: MockerFixture):
    # given
    pom_xml = "some/pom-path/pom.xml"
    mock_glob.return_value = [pom_xml]
    mocker.patch("xml.etree.ElementTree.parse").return_value = ElementTree(XML(mock_top_level_pom))
    mock_et_write = mocker.patch("xml.etree.ElementTree.ElementTree.write")
    new_pom_version = "4.11.0-SNAPSHOT"

    # when
    with pytest.raises(ValueError,
                       match=f'New POM version of {new_pom_version} must be > 4.11.1-SNAPSHOT - cannot update'):
        under_test.update_pom_versions("some/pom-path/", new_pom_version)

    # then
    mock_et_write.assert_not_called()
