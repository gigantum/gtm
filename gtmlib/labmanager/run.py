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

import docker

class LabManagerRunner(object):
    """Class to manage the launch of a labbook container.
    """

    def __init__(self, image_name: str, show_output: bool=False):
        self.docker_client = docker.from_env()
        self.image_name = image_name
        self.docker_image = self.docker_client.images.get(image_name)
        self.show_output = show_output

        if not self.docker_image:
            raise ValueError("Image name `{}' does not exist.".format(image_name))

    @property
    def is_running(self):
        """Return True if a container by given name exists with `docker ps -a`. """
        return any([container.name == self.image_name for container in self.docker_client.containers.list()])

    def stop(self, cleanup: bool=True):
        """Stop the docker container by this name. """
        if not self.is_running:
            raise ValueError("Cannot stop container that is not running.")
        else:
            containers = list(filter(lambda c: c.name == self.image_name, self.docker_client.containers.list()))
            assert len(containers) == 1
            containers[0].stop()
            if cleanup:
                self.docker_client.containers.prune()


    def launch(self):
        """Launch the docker container. """

        port_mapping = {'5000/tcp': 5000}
        volume_mapping = {
            os.path.join(os.path.expanduser("~"), "gigantum"): '/mnt/gigantum',
            '/var/run/docker.sock': '/var/run/docker.sock'
        }

        self.docker_client.containers.run(image=self.docker_image,
                                          detach=True,
                                          name=self.image_name,
                                          init=True,
                                          ports=port_mapping,
                                          volumes=volume_mapping)
