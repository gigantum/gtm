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


class LabManagerTester(object):
    """Class to manage testing of newly built container.
    """

    def __init__(self, container_name: str):
        self.docker_client = docker.from_env()
        self.container_name = container_name

    def _retrieve_container(self):
        """Return container from name. """
        cns = [c for c in self.docker_client.containers.list() if c.name == self.container_name]
        if len(cns) != 1:
            raise ValueError("Container by name `{}' not found.".format(self.container_name))
        else:
            return cns[0]

    def test(self) -> bool:
        """ Return True if all unit tests for labmanager pass.

        Note: Throws ValueError if the container does not exist.
        """

        container = self._retrieve_container()
        container.exec_run("cd /opt && py.test")