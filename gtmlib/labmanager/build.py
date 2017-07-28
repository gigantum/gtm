# Copyright (c) 2017 FlashX, LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os
import re
from pkg_resources import resource_filename

from git import Repo
import docker
from docker.errors import ImageNotFound
import yaml

from gtmlib.common import ask_question


class Build(object):
    """Class to manage building the labmanager container
    """
    def __init__(self):
        """Constructor"""
        self._image_name = None
        self._container_name = None
        self._ui_build_image_name = "gigantum/labmanager-ui-builder"

    def _get_current_commit_hash(self) -> str:
        """Method to get the current commit hash of the gtm repository

        Returns:
            str
        """
        # Get the path of the root directory
        file_path = resource_filename("gtmlib", "labmanager")
        file_path = file_path.rsplit(os.path.sep, 2)[0]
        repo = Repo(file_path)
        return repo.head.commit.hexsha

    def _generate_image_name(self) -> str:
        """Method to generate a name for the Docker Image

        Returns:
            str
        """
        return "labmanager-{}".format(self._get_current_commit_hash()[:8])

    def _generate_container_name(self) -> str:
        """Method to generate a name for the Docker container

        Returns:
            str
        """
        return "labmanager-{}".format(self._get_current_commit_hash()[:8])

    @property
    def image_name(self) -> str:
        """Get the name of the LabManager image

        Returns:
            str
        """
        if not self._image_name:
            self._image_name = self._generate_image_name()
        return self._image_name

    @image_name.setter
    def image_name(self, value: str) -> None:
        # Validate
        if not re.match("^(?!-)(?!.*--)[A-Za-z0-9-]+(?<!-)$", value):
            raise ValueError("Invalid image name provided. Only A-Za-z0-9- allowed w/ no leading or trailing hyphens.")

        self._image_name = value

    @property
    def container_name(self) -> str:
        """Get the name of the LabManager container

        Returns:
            str8
        """
        if not self._container_name:
            self._container_name = self._generate_container_name()
        return self._container_name

    @container_name.setter
    def container_name(self, value: str) -> None:
        # Validate
        if not re.match("^(?!-)(?!.*--)[A-Za-z0-9-]+(?<!-)$", value):
            raise ValueError("Invalid container name provided. Only A-Za-z0-9- allowed w/ no leading/trailing hyphens.")

        self._container_name = value

    def image_exists(self, name) -> bool:
        """Method to check if a Docker image exists

        Returns:
            bool
        """
        client = docker.from_env()

        # Check if image exists
        try:
            client.images.get(name)
            return True
        except ImageNotFound:
            return False

    def build_image(self, show_output: bool=False) -> None:
        """Method to build the Docker Image

        Returns:
            None
        """
        client = docker.from_env()

        # Check if image exists
        if self.image_exists(self.image_name):
            if ask_question("Image `{}` already exists. Do you wish to rebuild it?".format(self.image_name)):
                # Image found. Delete it to allow rebuild
                self.remove_image(self.image_name)
            else:
                # User said no
                raise ValueError("User aborted build due to duplicate image name.")

        print("\n*** Building frontend build image {}, please wait...\n\n".format(self._ui_build_image_name))

        # Rebuild front-end image to get latest sw
        if self.image_exists(self._ui_build_image_name):
            self.remove_image(self._ui_build_image_name)

        # Make sure build dir exists
        docker_file_dir = os.path.expanduser(os.path.join(resource_filename("gtmlib", "resources"), "frontend_build"))
        if not os.path.isdir(os.path.join(docker_file_dir, "build")):
            os.makedirs(os.path.join(docker_file_dir, "build"))

        # Build frontend image
        if show_output:
            [print(ln[list(ln.keys())[0]], end='') for ln in client.api.build(path=docker_file_dir,
                                                                              tag=self._ui_build_image_name,
                                                                              pull=True, rm=True,
                                                                              stream=True, decode=True)]
        else:
            client.images.build(path=docker_file_dir, tag=self._ui_build_image_name, pull=True, rm=True)

        print("\n\n*** Compiling frontend...\n\n")
        # Run frontend_build container to build frontend
        if show_output:
            container = client.containers.run(self._ui_build_image_name,
                                              detach=True, init=True,
                                              volumes={os.path.join(docker_file_dir, "build"):
                                                           {'bind': '/opt/labmanager-ui/build', 'mode': 'rw'}})
            [print(ln.decode("UTF-8")) for ln in container.attach(stream=True, logs=True)]
        else:
            client.containers.run(self._ui_build_image_name, detach=False, init=True,
                                  volumes={os.path.join(docker_file_dir, "build"):
                                           {'bind': '/opt/labmanager-ui/build', 'mode': 'rw'}})

        # Get Dockerfile directory
        docker_file_dir = os.path.expanduser(os.path.join(resource_filename("gtmlib", "resources")))

        # Write updated config file
        base_config_file = os.path.join(docker_file_dir, "submodules", 'labmanager-common', 'lmcommon', 'configuration',
                                        'config', 'labmanager.yaml.default')
        overwrite_config_file = os.path.join(docker_file_dir, 'labmanager-config-override.yaml')
        final_config_file = os.path.join(docker_file_dir, 'labmanager-config.yaml')

        with open(base_config_file, "rt") as cf:
            base_data = yaml.load(cf)
        with open(overwrite_config_file, "rt") as cf:
            overwrite_data = yaml.load(cf)

        # Merge sub-sections together
        for key in base_data:
            if key in overwrite_data:
                base_data[key].update(overwrite_data[key])

        # Write out updated config file
        with open(final_config_file, "wt") as cf:
            cf.write(yaml.dump(base_data, default_flow_style=False))

        # Build image
        print("\n\n*** Building LabManager image `{}`, please wait...\n\n".format(self.image_name))
        if show_output:
            [print(ln[list(ln.keys())[0]], end='') for ln in client.api.build(path=docker_file_dir,
                                                                              tag=self.image_name,
                                                                              pull=True, rm=True,
                                                                              stream=True, decode=True)]
        else:
            client.images.build(path=docker_file_dir, tag=self.image_name, pull=True)

    def remove_image(self, image_name: str) -> None:
        """Remove a docker image by name

        Args:
            image_name(str): Name of the docker image to remove

        Returns:
            None
        """
        client = docker.from_env()
        client.images.remove(image_name)
