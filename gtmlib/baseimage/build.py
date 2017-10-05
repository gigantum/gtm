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


class BaseImageBuilder(object):
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

    def _update_tracking_file(self, image_tag: str, built: bool, published: bool) -> None:
        """Method to update the status of an image in the tracking file

        Args:
            built(bool): Flag indicating if the image has been built
            published(bool): Flag indiciating if the image has been published
            image_tag(str): Name of the built image

        Returns:
            None
        """
        if os.path.isfile(self.tracking_file):
            with open(self.tracking_file, "rt") as f:
                data = json.load(f)

        else:
            # No tracking file exists
            data = {}

        # Update the dictionary setting publish to False
        data[image_tag] = {"build": built, "publish": published}

        with open(self.tracking_file, "wt") as f:
            json.dump(data, f)

    def _build_image(self, build_dir: str, verbose=False) -> str:
        """

        Args:
            build_dir:

        Returns:

        """
        client = docker.from_env()

        # Generate tags for both the named and latest versions
        base_tag = "gigdev/{}".format(os.path.basename(os.path.normpath(build_dir)))

        # TODO: remove temporary namespace reference when moving public
        #base_tag = "gigantum/{}".format(os.path.basename(os.path.normpath(build_dir)))
        named_tag = "{}:{}".format(base_tag, self._generate_image_tag_suffix())

        if verbose:
            [print(ln[list(ln.keys())[0]], end='') for ln in client.api.build(path=build_dir,
                                                                              tag=named_tag,
                                                                              pull=True, rm=True,
                                                                              stream=True, decode=True)]
        else:
            client.images.build(path=build_dir, tag=named_tag, pull=True)

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

    def build(self, image_name: str = None, verbose=False) -> None:
        """Method to build all, or a single image based on the dockerfiles stored within the base-image submodule

        Args:
            image_name(str): Name of a base image to build. If omitted all are built

        Returns:
            None
        """
        build_dirs = []
        if not image_name:
            # Find all images to build in the base_image submodule ref
            docker_file_dir = os.path.join(resource_filename('gtmlib', 'resources'), 'submodules', 'base-images')
            build_dirs = glob.glob(os.path.join(docker_file_dir,
                                                "*"))
            build_dirs = [x for x in build_dirs if os.path.isdir(x) is True]

        else:
            possible_build_dir = os.path.join(resource_filename('gtmlib', 'resources'), 'submodules',
                                              'base-images', image_name)
            if os.path.isdir(possible_build_dir):
                build_dirs.append(possible_build_dir)
            else:
                raise ValueError("Image `{}` not found.".format(image_name))

        if not build_dirs:
            raise ValueError("No images to build")

        for cnt, build_dir in enumerate(build_dirs):
            print("({}/{}) Building Base Image: {}".format(cnt+1, len(build_dirs),
                                                           os.path.basename(os.path.normpath(build_dir))))
            # Build each image
            image_tag = self._build_image(build_dir, verbose)

            # Update tracking file
            self._update_tracking_file(image_tag, built=True, published=False)

            print(" - Complete")
            print(" - Tag: {}".format(image_tag))

    def publish(self, image_name: str = None, verbose=False) -> None:
        """Method to publish images and update the Environment Repository

        Args:
            image_name(str): Name of a base image to build. If omitted all are built

        Returns:
            None
        """
        # Open tracking file
        if os.path.isfile(self.tracking_file):
            with open(self.tracking_file, "rt") as f:
                tracking_data = json.load(f)
        else:
            raise ValueError("You must first build images locally before publishing")

        if image_name:
            # Prune out all but the image to publish
            if image_name in tracking_data:
                tracking_data = tracking_data[image_name]
            else:
                raise ValueError("Image `{}` not found.".format(image_name))

        num_images = len((list(tracking_data.keys())))
        for cnt, image_tag in enumerate(list(tracking_data.keys())):
            print("({}/{}) Publishing Base Image: {}".format(cnt+1, num_images, image_tag))

            # Publish each image
            self._publish_image(image_tag, verbose)

            # TODO Update YAML def

            # Update tracking file
            self._update_tracking_file(image_tag, built=True, published=True)

            print(" - Complete")
            print(" - Tag: {}".format(image_tag))
