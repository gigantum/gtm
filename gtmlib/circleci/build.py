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
import json
import glob
from datetime import datetime
from pkg_resources import resource_filename

from git import Repo
import docker
from docker.errors import ImageNotFound, NotFound


class CircleCIImageBuilder(object):
    """Class to manage building base images
    """
    def __init__(self):
        """

        """
        self.tracking_file = os.path.join(self._get_gtm_dir(), ".image-build-status.json")

    def _get_gtm_dir(self) -> str:
        """Method to get the root gtm directory

        Returns:
            str
        """
        file_path = resource_filename("gtmlib", "common")
        return file_path.rsplit(os.path.sep, 2)[0]

    def _get_current_commit_hash(self) -> str:
        """Method to get the current commit hash of the gtm repository

        Returns:
            str
        """
        # Get the path of the root directory
        repo = Repo(self._get_gtm_dir())
        return repo.head.commit.hexsha

    def _generate_image_tag_suffix(self) -> str:
        """Method to generate a suffix for an image tag

        Returns:
            str
        """
        return "{}-{}".format(self._get_current_commit_hash()[:8], str(datetime.utcnow().date()))

    def _build_image(self, docker_file: str, docker_repo_name: str, verbose=False, no_cache=False) -> str:
        """

        Args:
            docker_file(str): name of the dockerfile to build
            docker_repo_name(str): name of the dockerhub repo to push to

        Returns:

        """
        client = docker.from_env()

        # Generate tags for both the named and latest versions
        docker_build_dir = os.path.expanduser(resource_filename("gtmlib", "resources"))

        base_tag = "gigantum/{}".format(docker_repo_name)
        named_tag = "{}:{}".format(base_tag, self._generate_image_tag_suffix())

        # If an image that could be the source for other images, you should pull, otherwise, you shouldn't
        if docker_repo_name in ['circleci-common']:
            pull = True
        else:
            pull = False

        if verbose:
            [print(ln[list(ln.keys())[0]], end='') for ln in client.api.build(path=docker_build_dir,
                                                                              dockerfile=docker_file,
                                                                              tag=named_tag,
                                                                              nocache=no_cache,
                                                                              pull=pull, rm=True,
                                                                              decode=True)]
        else:
            client.images.build(path=docker_build_dir,  dockerfile=docker_file, tag=named_tag,
                                pull=True, nocache=no_cache)

        # Tag with latest in case images depend on each other. Will not get published.
        client.images.get(named_tag).tag(f"{base_tag}:latest")

        # Verify the desired image built successfully
        try:
            client.images.get(named_tag)
        except NotFound:
            raise ValueError("Image Build Failed!")

        return named_tag

    def _publish_image(self, image_tag: str, verbose=False) -> None:
        """Private method to push images to the logged in server (e.g hub.docker.com)

        Args:
            image_tag(str): full image tag to publish

        Returns:
            None
        """
        client = docker.from_env()

        # Split out the image and the tag
        image, tag = image_tag.split(":")

        if verbose:
            [print(ln[list(ln.keys())[0]], end='') for ln in client.api.push(image, tag=tag,
                                                                             stream=True, decode=True)]
        else:
            client.images.push(image, tag=tag)

    def build(self, repo_name: str = None, verbose=False, no_cache=False) -> None:
        """Method to build all, or a single image based on the dockerfiles stored within the base-image submodule

        Args:
            repo_name(str): Name of the repository you are building a container to test
            verbose(bool): flag indication if output should print to the console
            no_cache(bool): flag indicating if the docker cache should be ignored

        Returns:
            None
        """
        images = {
            'lmcommon': {
                "docker_file": "Dockerfile_circleci_lmcommon",
                "docker_repo": "circleci-common"
            },
            'labmanager-service-labbook': {
                "docker_file": "Dockerfile_circleci_service_labbook",
                "docker_repo": "circleci-service-client"
            },
        }

        if repo_name not in images:
            raise ValueError(f"Unsupported repository name: {repo_name}")

        # Build image
        print(f"Building CircleCI Docker image for repository: {repo_name}")
        image_tag = self._build_image(images[repo_name]['docker_file'],
                                      images[repo_name]['docker_repo'],
                                      verbose=verbose, no_cache=no_cache)

        # Publish to dockerhub
        print(f"Publishing CircleCI Docker image to DockerHub: {image_tag}")
        self._publish_image(image_tag, verbose)

        print("Done!")
        print(f"** Update `.circleci/config.yml` in {repo_name} to point to {image_tag} and "
              f"commit to run tests with new container **")
