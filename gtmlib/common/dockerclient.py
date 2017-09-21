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
import socket
import json
import os
import docker


def _get_docker_server_api_version() -> str:
    """Retrieve the Docker server API version. """

    socket_path = '/var/run/docker.sock'
    if not os.path.exists(socket_path):
        raise ValueError('No docker.sock on machine (is a Docker server installed?)')

    socket_connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    socket_connection.connect(socket_path)
    socket_connection.send(b'GET http://*/version HTTP/1.1\r\nHost: *\r\n\r\n')

    response_data = socket_connection.recv(4000)
    content_lines = response_data.decode().split('\r\n')

    version_dict = json.loads(content_lines[-1])
    if 'ApiVersion' not in version_dict.keys():
        raise ValueError('ApiVersion not in Docker version config data')
    else:
        return version_dict['ApiVersion']


def get_docker_client(check_server_version=True, fallback=True):
    """Return a docker client with proper version to match server API. """

    if check_server_version:
        try:
            docker_server_api_version = _get_docker_server_api_version()
            return docker.from_env(version=docker_server_api_version)
        except ValueError as e:
            if fallback:
                return docker.from_env()
            else:
                raise e
    else:
        return docker.from_env()

