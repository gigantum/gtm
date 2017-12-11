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
import platform
import shutil
import glob
import datetime
import sys

from git import Repo
from docker.errors import ImageNotFound, NotFound
import yaml

from gtmlib.common import ask_question, dockerize_path, get_docker_client, DockerVolume


class LabManagerBuilder(object):
    """Class to manage building the labmanager container
    """
    def __init__(self):
        """Constructor"""
        self._image_name = None
        self._container_name = None
        self._ui_build_image_name = "gigantum/labmanager-ui-builder"
        self.docker_client = get_docker_client()

        self.node_volume = DockerVolume("labmanager_prod_node_build_vol", client=self.docker_client)

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
        return "gigantum/labmanager"

    def _remove_pyc(self, directory: str) -> None:
        """Method to remove all pyc files recursively

        Args:
            directory(str) Root directory to walk

        Returns:

        """
        for filename in glob.glob('{}/**/*.pyc'.format(directory), recursive=True):
                os.remove(filename)

    def get_image_tag(self) -> str:
        """Method to generate a named tag for the Docker Image

        Returns:
            str
        """
        return self._get_current_commit_hash()[:8]

    def _generate_container_name(self) -> str:
        """Method to generate a name for the Docker container

        Returns:
            str
        """
        return self.image_name.replace("/", ".")

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
        if not re.match("^(?![-/])(?!.*--)[A-Za-z0-9_/-]+(?<![-/])$", value):
            raise ValueError("Invalid image name provided. Only A-Za-z0-9/- allowed.")

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
        if not re.match("^(?![-\.])(?!.*--)[A-Za-z0-9_.-]+(?<![-\.])$", value):
            raise ValueError("Invalid container name. Only A-Za-z0-9._- allowed w/ no leading/trailing hyphens.")

        self._container_name = value

    def image_exists(self, name) -> bool:
        """Method to check if a Docker image exists

        Returns:
            bool
        """
        # Check if image exists
        try:
            self.docker_client.images.get(name)
            return True
        except ImageNotFound:
            return False

    def remove_image(self, image_name: str) -> None:
        """Remove a docker image by name

        Args:
            image_name(str): Name of the docker image to remove

        Returns:
            None
        """
        # Remove stopped container if it exists
        self.prune_container(image_name)

        # Remove image
        self.docker_client.images.remove(image_name)

    def prune_container(self, container_name: str) -> None:
        """Remove a docker container by name

        Args:
            container_name(str): Name of the docker container to remove

        Returns:
            None
        """
        # Remove stopped container if it exists
        try:
            # Replace / with . if the repo is in the image name
            container_name = container_name.replace("/", ".")

            build_container = self.docker_client.containers.get(container_name)
            build_container.remove()
        except NotFound:
            pass

    def build_image(self, show_output: bool=False, no_cache: bool=False) -> None:
        """Method to build the LabManager Docker Image

        Returns:
            None
        """
        self.docker_client = get_docker_client()

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

        # Rebuild front-end image to get latest sw dependencies if desired
        build_ui_container = True
        if self.image_exists(self._ui_build_image_name):
            if ask_question("\nFrontend build container already exists. Do you want to rebuild it?".format(self.image_name)):
                print("*** Building frontend build image {}, please wait...\n".format(self._ui_build_image_name))
                # Remove so you can rebuild
                self.remove_image(self._ui_build_image_name)
                build_ui_container = True
            else:
                build_ui_container = False

        # Setup docker volume that will hold the node packages
        if self.node_volume.exists():
            if ask_question("\nNode Packages already installed. Do you want to rebuild from scratch?"):
                print("*** Removing node package install\n")
                self.node_volume.remove()
                self.node_volume.create()
        else:
            # Create an empty volume
            self.node_volume.create()

        docker_build_dir = os.path.expanduser(resource_filename("gtmlib", "resources"))
        frontend_dir = os.path.join(docker_build_dir, 'submodules', 'labmanager-ui')

        if build_ui_container:
            # Build frontend image
            if show_output:
                [print(ln[list(ln.keys())[0]], end='') for ln in self.docker_client.api.build(path=docker_build_dir,
                                                                                  dockerfile='Dockerfile_frontend_build',
                                                                                  tag=self._ui_build_image_name,
                                                                                  pull=True, rm=True,
                                                                                  stream=True, decode=True,
                                                                                  nocache=no_cache)]
            else:
                self.docker_client.images.build(path=docker_build_dir, dockerfile='Dockerfile_frontend_build',
                                    tag=self._ui_build_image_name, pull=True, rm=True, nocache=no_cache)

        # Compile frontend application into gtmlib/resources/frontend_resources/build
        print("\n*** Updating node packages and compiling frontend application...\n\n")
        container_name = self._ui_build_image_name.replace("/", ".")
        self.prune_container(container_name)

        # Copy labmanager-ui to temp dir WITHOUT node packages
        temp_ui_dir = os.path.join(docker_build_dir, 'frontend_resources', 'build')
        if os.path.exists(temp_ui_dir):
            shutil.rmtree(temp_ui_dir)
        shutil.copytree(frontend_dir, temp_ui_dir + os.path.sep, ignore=shutil.ignore_patterns("node_modules"))

        if os.path.exists(os.path.join(temp_ui_dir, 'build')):
            # Remove build dir in root of UI code
            shutil.rmtree(os.path.join(temp_ui_dir, 'build'))

        # convert to docker mountable volume name (needed for non-POSIX fs)
        dkr_vol_path = dockerize_path(temp_ui_dir)

        volumes = {dkr_vol_path: {'bind': '/mnt/labmanager-ui', 'mode': 'rw'},
                   self.node_volume.volume_name: {
                       "bind": '/opt/build_dir/node_modules',
                       'mode': 'rw'}
                   }

        if platform.system() == 'Windows':
            environment_vars = {'WINDOWS_HOST': 1}
            environment_vars = {'LOCAL_USER_ID': 9001}
        else:
            environment_vars = {'LOCAL_USER_ID': os.getuid()}

        if show_output:
            container = self.docker_client.containers.run(self._ui_build_image_name,
                                                          name=container_name,
                                                          detach=True, init=True,
                                                          environment=environment_vars,
                                                          volumes=volumes)

            [print(ln.decode("UTF-8"), end='') for ln in container.attach(stream=True, logs=True)]
        else:
            # launch the ui build container
            self.docker_client.containers.run(self._ui_build_image_name,
                                              name=container_name, detach=False,
                                              init=True, environment=environment_vars, volumes=volumes)

        # Verify build succeeded
        if not os.path.exists(os.path.join(temp_ui_dir, 'build', 'service-worker.js')):
            print("** Error: Frontend build failed! ***")
            sys.exit(1)

        # Copy build dir back to submodules/labmanager-ui
        ui_dest_dir = os.path.join(frontend_dir, 'build')
        if os.path.exists(ui_dest_dir):
            shutil.rmtree(ui_dest_dir)
        shutil.copytree(os.path.join(temp_ui_dir, 'build'), ui_dest_dir)
        # Clean up temp copy of code
        shutil.rmtree(temp_ui_dir)

        # Build LabManager container
        # Write updated config file
        base_config_file = os.path.join(docker_build_dir, "submodules", 'labmanager-common', 'lmcommon',
                                        'configuration', 'config', 'labmanager.yaml.default')
        overwrite_config_file = os.path.join(docker_build_dir, 'labmanager_resources',
                                             'labmanager-config-override.yaml')
        final_config_file = os.path.join(docker_build_dir, 'labmanager_resources', 'labmanager-config.yaml')

        with open(base_config_file, "rt") as cf:
            base_data = yaml.load(cf)
        with open(overwrite_config_file, "rt") as cf:
            overwrite_data = yaml.load(cf)

        # Merge sub-sections together
        for key in base_data:
            if key in overwrite_data:
                base_data[key].update(overwrite_data[key])

        # Add Build Info
        base_data['build_info'] = {'application': "LabManager",
                                   'built_on': str(datetime.datetime.utcnow()),
                                   'revision': self._get_current_commit_hash()}

        # Write out updated config file
        with open(final_config_file, "wt") as cf:
            cf.write(yaml.dump(base_data, default_flow_style=False))

        # Image Labels
        labels = {'io.gigantum.app': 'labmanager',
                  'io.gigantum.maintainer.email': 'hello@gigantum.io'}

        # Delete .pyc files in case dev tools used on something not ubuntu before building
        self._remove_pyc(os.path.join(docker_build_dir, "submodules", 'labmanager-common', 'lmcommon'))
        self._remove_pyc(os.path.join(docker_build_dir, "submodules", 'labmanager-service-labbook', 'lmsrvcore'))
        self._remove_pyc(os.path.join(docker_build_dir, "submodules", 'labmanager-service-labbook', 'lmsrvlabbook'))

        # Build image
        print("\n\n*** Building LabManager image `{}`, please wait...\n\n".format(self.image_name))
        if show_output:
            [print(ln[list(ln.keys())[0]], end='') for ln in self.docker_client.api.build(path=docker_build_dir,
                                                                              dockerfile='Dockerfile_labmanager',
                                                                              tag=named_image,
                                                                              labels=labels, nocache=no_cache,
                                                                              pull=True, rm=True,
                                                                              stream=True, decode=True)]
        else:
            self.docker_client.images.build(path=docker_build_dir, dockerfile='Dockerfile_labmanager',
                                tag=named_image, nocache=no_cache,
                                pull=True, labels=labels)

        # Tag with `latest` for auto-detection of image on launch
        self.docker_client.api.tag(named_image, 'gigantum/labmanager', 'latest')

    def publish(self, image_tag: str = None, verbose=False) -> None:
        """Method to push image to the logged in image repository server (e.g hub.docker.com)

        Args:
            image_tag(str): full image tag to publish

        Returns:
            None
        """
        # If no tag provided, use current repo hash
        if not image_tag:
            image_tag = self.get_image_tag()

        if verbose:
            [print(ln[list(ln.keys())[0]]) for ln in self.docker_client.api.push('gigantum/labmanager', tag=image_tag,
                                                                             stream=True, decode=True)]
        else:
            self.docker_client.images.push('gigantum/labmanager', tag=image_tag)

        self.docker_client.images.push('gigantum/labmanager', tag='latest')

    def cleanup(self, dev_images=False):
        """Method to clean up old gigantum/labmanager images

        Args:
            dev_images(bool): If true, cleanup gigantum/labmanager-dev images instead

        Returns:
            None
        """
        if dev_images:
            image_name = "gigantum/labmanager-dev"
        else:
            image_name = "gigantum/labmanager"

        images = self.docker_client.images.list(image_name)

        cnt = 0
        for image in images:
            if any(['latest' in x for x in image.tags]):
                continue
            cnt += 1

        if cnt == 0:
            print(f" - No old {image_name} images to remove\n")
            return None

        if not ask_question(f"\nDo you want to remove {cnt} old {image_name} images?"):
            print(" - Prune operation cancelled\n")
            return None

        print(f"\nRemoving old {image_name} images:")
        for image in images:
            if any(['latest' in x for x in image.tags]):
                continue
            print(f" - Removing {image.tags[0]}")
            self.docker_client.images.remove(image.id)
