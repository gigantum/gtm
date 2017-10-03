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
import pytest
from gtmlib.common import dockerclient
from docker.errors import NotFound

from gtmlib.common import DockerVolume


@pytest.fixture()
def setup_docker_vol():
    """Fixture to create a Build instance with a test image name that does not exist and cleanup after"""
    client = dockerclient.get_docker_client()
    vol = client.volumes.create(name='test-labmanager-volume')

    yield 'test-labmanager-volume', client

    # Remove image post test if it still exists
    vol.remove()

@pytest.fixture()
def cleanup_docker_vol():
    """Fixture to create a Build instance with a test image name that does not exist and cleanup after"""
    yield 'test-labmanager-volume'

    # Remove image post test if it still exists
    client = dockerclient.get_docker_client()
    try:
        vol = client.volumes.get('test-labmanager-volume')
        vol.remove()
    except NotFound:
        pass


class TestLabManagerBuild(object):
    def test_does_not_exist(self):
        """Test checking for a docker volume that does not exist"""
        dv = DockerVolume("adfdsfgdfsglsdflgdsflgj")

        assert dv.exists() is False

    def test_does_exist(self, setup_docker_vol):
        """Test checking for a docker volume that does exist"""
        dv = DockerVolume(setup_docker_vol[0], client=setup_docker_vol[1])

        assert dv.exists() is True

    def test_create(self, cleanup_docker_vol):
        """Test checking for a docker volume that does exist"""
        dv = DockerVolume(cleanup_docker_vol)

        assert dv.exists() is False

        dv.create()

        assert dv.exists() is True

    def test_remove(self, cleanup_docker_vol):
        """Test checking for a docker volume that does exist"""
        dv = DockerVolume(cleanup_docker_vol)

        assert dv.exists() is False

        dv.create()

        assert dv.exists() is True

        dv.remove()

        assert dv.exists() is False

