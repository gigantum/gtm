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
import typing
import docker

from docker.errors import NotFound

from gtmlib.common import get_docker_client


class DockerVolume(object):
    """Class to manage docker volumes used within the build system
    """
    def __init__(self, volume_name: str, client=None) -> None:
        self.volume_name = volume_name

        if not client:
            self.client = get_docker_client()
        else:
            self.client = client

    def exists(self) -> bool:
        """Check if a docker volume exists

        Returns:
            bool
        """
        try:
            self.client.volumes.get(self.volume_name)
            return True
        except NotFound:
            return False

    def create(self) -> None:
        """Create the volume

        Returns:
            None
        """
        self.client.volumes.create(self.volume_name)

    def remove(self) -> None:
        """Remove the volume

        Returns:
            None
        """
        volume = self.client.volumes.get(self.volume_name)
        volume.remove()
