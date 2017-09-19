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

import docker
import yaml

from gtmlib.common import ask_question
from gtmlib.common import dockerize_volume_path
from gtmlib.labmanager.build import LabManagerBuilder


class LabManagerDevBuilder(LabManagerBuilder):
    """Class to manage building the labmanager container
    """
    def _generate_image_name(self) -> str:
        """Method to generate a name for the Docker Image

        Returns:
            str
        """
        return "gigantum/labmanager-dev"

    def build_image(self, show_output: bool=False) -> None:
        """Method to build the LabManager Dev Docker Image

        Returns:
            None
        """
        client = docker.from_env()

        # Check if image exists
        named_image = "{}:{}".format(self.image_name, self.get_image_tag())
        if self.image_exists(named_image):
            if ask_question("Image `{}` already exists. Do you wish to rebuild it?".format(named_image)):
                # Image found. Make sure container isn't running.
                self.prune_container(named_image)
                pass
            else:
                # User said no
                raise ValueError("User aborted build due to duplicate image name.")

        docker_build_dir = os.path.expanduser(resource_filename("gtmlib", "resources"))

        # Build LabManager container
        # Write updated config file
        base_config_file = os.path.join(docker_build_dir, "submodules", 'labmanager-common', 'lmcommon',
                                        'configuration', 'config', 'labmanager.yaml.default')
        overwrite_config_file = os.path.join(docker_build_dir, 'labmanager_dev_resources',
                                             'labmanager-config-override.yaml')
        final_config_file = os.path.join(docker_build_dir, 'labmanager_dev_resources', 'labmanager-config.yaml')

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
        print("\n\n*** Building LabManager image `{}`, please wait...\n\n".format(self.image_name))
        if show_output:
            [print(ln[list(ln.keys())[0]], end='') for ln in client.api.build(path=docker_build_dir,
                                                                              dockerfile='Dockerfile_labmanager_dev',
                                                                              tag=named_image,
                                                                              labels=labels,
                                                                              pull=True, rm=True,
                                                                              stream=True, decode=True)]
        else:
            client.images.build(path=docker_build_dir, dockerfile='Dockerfile_labmanager_dev',
                                tag=named_image,
                                pull=True, labels=labels)

        # Tag with `latest` for auto-detection of image on launch
        client.api.tag(named_image, self._generate_image_name(), 'latest')

        ui_app_dir = os.path.join(docker_build_dir, "submodules", 'labmanager-ui')
        if os.path.exists(os.path.join(ui_app_dir, 'node_modules')):
            if ask_question("Do you wish to re-install node packages?"):
                # Use container to run npm install into the labmanager-ui repo
                print("\n*** Installing node packages to run UI in debug mode...this will take awhile...\n\n")
                ui_app_dir = os.path.join(docker_build_dir, "submodules", 'labmanager-ui')
                container_name = uuid.uuid4().hex

                # convert to docker mountable volume name (needed for non-POSIX fs)
                dkr_vol_path = dockerize_volume_path(ui_app_dir)

                if platform.system() == 'Windows':
                    environment_vars = {}
                else:
                    environment_vars = {'LOCAL_USER_ID': os.getuid()}

                command = 'sh -c "cd /mnt/build && npm install && npm run relay"'

                # launch the dev container
                client.containers.run(self.image_name,
                                      command=command,
                                      name=container_name,
                                      detach=False,
                                      init=True,
                                      environment=environment_vars,
                                      volumes={dkr_vol_path: {'bind': '/mnt/build', 'mode': 'rw'}})

                print(" - Done.")


