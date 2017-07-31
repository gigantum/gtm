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

import docker

class LabManagerRunner(object):
    """Class to manage the launch of a labbook container.
    """

    def __init__(self, image_name: str):
        self.docker_client = docker.from_env()
        self.image_name = image_name
        self.docker_image = self.docker_client.images.get(image_name)

        if not self.docker_image:
            raise ValueError("Image name `{}' does not exist.".format(image_name))

    def launch(self):
        """Launch the docker container. """
        # Note: This is the command needed to be replicated programmatically...
        #   docker run -d --name <image name> --init -p 5000:5000 -v "<local working dir>:/mnt/gigantum" \
        #   -v /var/run/docker.sock:/var/run/docker.sock
        docker_client = docker.from_env()

        docker_client.images[self.image_name]