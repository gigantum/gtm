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


class Compose(object):
    """Class to manage building the labmanager container
    """

    def prompt_with_default(self, question, default):
        """

        Args:
            question:
            default:

        Returns:

        """
        print("{} [{}]: ".format(question, default), end="")
        choice = input().lower().strip()

        if not choice:
            choice = default

        return choice

    def generate_backend_yaml_file(self) -> None:
        """Method to build the docker compose file for a user

        Returns:
            None
        """
        print("Generating docker-compose.yml for backend dev with PyCharm\n\n")

        # Set working dir
        working_dir = self.prompt_with_default("LabManager Working Directory",
                                               os.path.expanduser(os.path.join("~", 'gigantum')))

        # Set user id
        uid = self.prompt_with_default("Desired User ID", os.getuid())

        # Load template
        template_file = os.path.join(resource_filename("gtmlib", "resources"),
                                     'labmanager_dev_resources', 'docker-compose-backend.yml.template')
        with open(template_file, 'rt') as template:
            data = template.read()

        # Replace values
        data = data.replace('{% WORKING_DIR %}', working_dir)
        data = data.replace('{% USER_ID %}', str(uid))

        # Write file
        output_file = os.path.join(resource_filename("gtmlib", "resources"),
                                   'labmanager_dev_resources', 'docker-compose-backend.yml')
        with open(output_file, 'wt') as out_file:
            out_file.write(data)

        print("Docker Compose file written to {}".format(output_file))
