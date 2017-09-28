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
import tarfile

import docker
import yaml

from gtmlib.common import ask_question, dockerize_volume_path, get_docker_client
from gtmlib.labmanager.build import LabManagerBuilder


class LabManagerDevBuilder(LabManagerBuilder):
    """Class to manage building the labmanager container
    """
    def __init__(self):
        LabManagerBuilder.__init__(self)
        self.docker_build_dir = os.path.expanduser(resource_filename("gtmlib", "resources"))
        self.ui_app_dir = os.path.join(self.docker_build_dir, "submodules", 'labmanager-ui')

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
            shutil.rmtree(os.path.join(self.ui_app_dir, 'node_modules'))

    def _unzip_node_modules(self) -> None:
        """

        Returns:

        """
        # Remove node dir if it exists
        self._remove_node_modules()
        print(" - Unzipping node_modules directory...")
        with zipfile.ZipFile(os.path.join(self.ui_app_dir, 'node_modules.zip'), "r") as z:
            z.extractall(self.ui_app_dir)

    def build_image(self, show_output: bool=False) -> None:
        """Method to build the LabManager Dev Docker Image

        Returns:
            None
        """
        client = get_docker_client()

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

        install_node = True
        # If the node_modules.zip file exists, we can reuse it
        if os.path.exists(os.path.join(self.ui_app_dir, 'node_modules.zip')):
            install_node = ask_question("\nDo you wish to re-install node packages locally?")

            if install_node:
                os.remove(os.path.join(self.ui_app_dir, 'node_modules.zip'))
                os.remove(os.path.join(self.ui_app_dir, 'src.zip'))

        # Delete node_packages directory because it hoses docker file share on mac
        self._remove_node_modules()

        # Build LabManager container
        # Write updated config file
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

        # Image Labels
        labels = {'io.gigantum.app': 'labmanager-dev',
                  'io.gigantum.maintainer.email': 'hello@gigantum.io'}

        # Build image
        print(" - Building LabManager image `{}`, please wait...".format(self.image_name))
        if show_output:
            [print(ln[list(ln.keys())[0]], end='') for ln in client.api.build(path=self.docker_build_dir,
                                                                              dockerfile='Dockerfile_developer',
                                                                              tag=named_image,
                                                                              labels=labels,
                                                                              pull=True, rm=True,
                                                                              stream=True, decode=True)]
        else:
            client.images.build(path=self.docker_build_dir, dockerfile='Dockerfile_developer',
                                tag=named_image,
                                pull=True, labels=labels)

        # Tag with `latest` for auto-detection of image on launch
        client.api.tag(named_image, self._generate_image_name(), 'latest')

        if install_node:
            # Use container to run npm install into the labmanager-ui repo
            print(" - Installing node packages to run UI in debug mode...this will take awhile...")
            ui_app_dir = os.path.join(self.docker_build_dir, "submodules", 'labmanager-ui')

            # convert to docker mountable volume name (needed for non-POSIX fs)
            dkr_vol_path = dockerize_volume_path(ui_app_dir)

            environment_vars = {"NPM_INSTALL": 1}
            if platform.system() != 'Windows':
                environment_vars['LOCAL_USER_ID'] = os.getuid()

            command = 'sh -c "cp -a /mnt/build/. /opt/node_build && cd /opt/node_build && npm install && npm run relay'
            command = '{} && zip -r node_modules.zip node_modules'.format(command)
            command = '{} && cp /opt/node_build/node_modules.zip /mnt/build'.format(command)
            command = '{} && zip -r src.zip src'.format(command)
            command = '{} && cp /opt/node_build/src.zip /mnt/build"'.format(command)

            # launch the dev container to install node packages
            client.containers.run(self.image_name,
                                  command=command,
                                  name=uuid.uuid4().hex,
                                  detach=False,
                                  init=True,
                                  environment=environment_vars,
                                  volumes={dkr_vol_path: {'bind': '/mnt/build', 'mode': 'rw'}})

            # Unzip into node_module dir
            self._unzip_node_modules()

            # Unzip src dir to get relay generated files
            with zipfile.ZipFile(os.path.join(self.ui_app_dir, 'src.zip'), "r") as z:
                z.extractall(self.ui_app_dir)

        else:
            # Unzip existing data
            self._unzip_node_modules()

        print(" - Done.")


