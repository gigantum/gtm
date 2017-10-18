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
from pkg_resources import resource_filename
import platform
import uuid
import shutil
import zipfile
import subprocess
import tarfile
import time
import typing

import docker
from docker.errors import NotFound
import yaml

from gtmlib.common import ask_question, dockerize_volume_path, get_docker_client, DockerVolume
from gtmlib.labmanager.build import LabManagerBuilder


class LabManagerDevBuilder(LabManagerBuilder):
    """Class to manage building the labmanager container
    """
    def __init__(self):
        LabManagerBuilder.__init__(self)
        self.docker_build_dir = os.path.expanduser(resource_filename("gtmlib", "resources"))
        self.ui_app_dir = os.path.join(self.docker_build_dir, "submodules", 'labmanager-ui')

        self.docker_client = get_docker_client()
        self.share_volume = DockerVolume("labmanager_share_vol", client=self.docker_client)
        self.node_volume = DockerVolume("labmanager_dev_node_build_vol", client=self.docker_client)

    def _generate_image_name(self) -> str:
        """Method to generate a name for the Docker Image

        Returns:
            str
        """
        return "gigantum/labmanager-dev"

    def _remove_node_modules(self) -> None:
        """

        Returns:

        """
        if os.path.exists(os.path.join(self.ui_app_dir, 'node_modules')):
            print(" - Removing node_modules directory.")
            shutil.rmtree(os.path.join(self.ui_app_dir, 'node_modules'), ignore_errors=True)

    def _unzip_node_modules(self) -> None:
        """

        Returns:

        """
        # Remove node dir if it exists
        self._remove_node_modules()
        print(" - Unzipping node_modules directory...")
        with zipfile.ZipFile(os.path.join(self.ui_app_dir, 'node_modules.zip'), "r") as z:
            z.extractall(self.ui_app_dir)

    def _generate_config_file(self) -> None:
        """Method to update the local config files

        Returns:
            None
        """
        base_config_file = os.path.join(self.docker_build_dir, "submodules", 'labmanager-common', 'lmcommon',
                                        'configuration', 'config', 'labmanager.yaml.default')
        overwrite_config_file = os.path.join(self.docker_build_dir, 'developer_resources',
                                             'labmanager-config-override.yaml')
        final_config_file = os.path.join(self.docker_build_dir, 'developer_resources', 'labmanager-config.yaml')

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

    @staticmethod
    def _get_docker_run_env_vars() -> typing.Dict[str, typing.Any]:
        """Method to get the run-time environment variables for docker

        Returns:

        """
        environment_vars = {"NPM_INSTALL": 1}
        if platform.system() != 'Windows':
            environment_vars['LOCAL_USER_ID'] = os.getuid()
        else:
            environment_vars['WINDOWS_HOST'] = 1

        return environment_vars

    def run_relay(self) -> None:
        """Method to build relay queries

        Returns:
            None
        """
        print(" - running `yarn relay`...")
        # convert to docker mountable volume name (needed for non-POSIX fs)
        dkr_vol_path = dockerize_volume_path(self.ui_app_dir)

        relay_container = None
        try:
            # Start container back up
            container_name = uuid.uuid4().hex
            relay_container = self.docker_client.containers.run(self.image_name,
                                                                command="sleep infinity",
                                                                name=container_name,
                                                                detach=True,
                                                                init=True,
                                                                environment=self._get_docker_run_env_vars(),
                                                                volumes={dkr_vol_path: {'bind': '/mnt/src',
                                                                                        'mode': 'rw'},
                                                                         self.node_volume.volume_name: {
                                                                             "bind": '/mnt/node_build',
                                                                             'mode': 'rw'}
                                                                         })

            # Run relay command
            command = 'sh -c "cp -a /mnt/src/src /mnt/node_build && cd /mnt/node_build && yarn relay"'
            exec_cmd = self.docker_client.api.exec_create(relay_container.name, command)
            result_gen = self.docker_client.api.exec_start(exec_cmd['Id'], stream=True)
            [print("    - {}".format(ln.decode()), end='') for ln in result_gen]

            # docker cp the files out
            subprocess.run(["docker", "cp",
                            '{}:/mnt/node_build/src/'.format(container_name),
                            self.ui_app_dir], stdout=subprocess.PIPE, check=True)

        finally:
            print(" - Cleaning up...")
            relay_container.stop(timeout=10)
            relay_container.remove()

    def build_image(self, show_output: bool=False, no_cache: bool=False) -> None:
        """Method to build the LabManager Dev Docker Image

        Returns:
            None
        """
        # Check if image exists
        named_image = "{}:{}".format(self.image_name, self.get_image_tag())
        if self.image_exists(named_image):
            if ask_question("\nImage `{}` already exists. Do you wish to rebuild it?".format(named_image)):
                # Image found. Make sure container isn't running.
                self.prune_container(named_image)
                pass
            else:
                # User said no
                raise ValueError("User aborted build due to duplicate image name.")

        # Check if the share volume exists
        if not self.share_volume.exists():
            self.share_volume.create()

        # Check if the node_build volume exists
        if self.node_volume.exists():
            # If the node_modules volume exists, check if you want to rebuild
            reinstall_node = ask_question("\nDo you wish to re-install node packages from scratch?")

            if reinstall_node:
                # Re-create the node_volume so it is empty
                self.node_volume.remove()
                self.node_volume.create()
        else:
            self.node_volume.create()

        # Delete node_packages directory because it hoses docker file share on mac
        self._remove_node_modules()

        # Build LabManager container
        # Write updated config file
        self._generate_config_file()

        # Image Labels
        labels = {'io.gigantum.app': 'labmanager-dev',
                  'io.gigantum.maintainer.email': 'hello@gigantum.io'}

        # Build image
        print(" - Building LabManager image `{}`, please wait...".format(self.image_name))
        if show_output:
            [print("    - {}".format(ln[list(ln.keys())[0]]),
                   end='') for ln in self.docker_client.api.build(path=self.docker_build_dir,
                                                                  dockerfile='Dockerfile_developer',
                                                                  tag=named_image,
                                                                  labels=labels, nocache=no_cache,
                                                                  pull=True, rm=True,
                                                                  stream=True, decode=True)]
        else:
            self.docker_client.images.build(path=self.docker_build_dir, dockerfile='Dockerfile_developer',
                                            tag=named_image, nocache=no_cache,
                                            pull=True, labels=labels)

        # Tag with `latest` for auto-detection of image on launch
        self.docker_client.api.tag(named_image, self._generate_image_name(), 'latest')

        # Use container to run npm install into the labmanager-ui repo
        print(" - Installing node packages to run UI in debug mode...this may take awhile...")

        # convert to docker mountable volume name (needed for non-POSIX fs)
        dkr_vol_path = dockerize_volume_path(self.ui_app_dir)

        command = 'sh -c "cp -a /mnt/src/* /mnt/node_build && cd /mnt/node_build && yarn install"'

        # launch the dev container to install node packages
        container_name = uuid.uuid4().hex

        if show_output:
            print("")
            build_container = self.docker_client.containers.run(self.image_name,
                                                                command=command,
                                                                name=container_name,
                                                                detach=True,
                                                                init=True,
                                                                environment=self._get_docker_run_env_vars(),
                                                                volumes={dkr_vol_path: {'bind': '/mnt/src',
                                                                                        'mode': 'rw'},
                                                                         self.node_volume.volume_name: {
                                                                             "bind": '/mnt/node_build',
                                                                             'mode': 'rw'}
                                                                         })

            log_data = build_container.logs(stream=True)
            [print("    - {}".format(ln.decode()), end='') for ln in log_data]
        else:
            build_container = self.docker_client.containers.run(self.image_name,
                                                                command=command,
                                                                name=container_name,
                                                                detach=True,
                                                                init=True,
                                                                environment=self._get_docker_run_env_vars(),
                                                                volumes={dkr_vol_path: {'bind': '/mnt/src',
                                                                                        'mode': 'rw'},
                                                                         self.node_volume.volume_name: {
                                                                             "bind": '/mnt/node_build',
                                                                             'mode': 'rw'}
                                                                         })

            while build_container.status == "running" or build_container.status == "created":
                time.sleep(2.5)
                build_container.reload()

        # Remove container (to be sure to release the volume)
        build_container.stop()
        build_container.remove()

        print(" - Copying node modules to host machine...")
        node_container = None
        try:
            # Start container back up
            node_container = self.docker_client.containers.run(self.image_name,
                                                               command="sleep infinity",
                                                               name=uuid.uuid4().hex,
                                                               detach=True,
                                                               init=True,
                                                               environment=self._get_docker_run_env_vars(),
                                                               volumes={dkr_vol_path: {'bind': '/mnt/src',
                                                                                       'mode': 'rw'},
                                                                        self.node_volume.volume_name: {
                                                                            "bind": '/mnt/node_build',
                                                                            'mode': 'rw'}
                                                                        })

            # Make node module dir if it doesn't exist
            node_dir = os.path.join(self.ui_app_dir, 'node_modules')
            if not node_dir:
                os.makedirs(node_dir)

            # docker cp the files out
            src_str = "{}:/mnt/node_build/node_modules".format(node_container.name)
            subprocess.run(["docker", "cp", src_str, node_dir], stdout=subprocess.PIPE, check=True)

        finally:
            node_container.stop()
            node_container.remove()

        self.run_relay()

        print(" - Done")


