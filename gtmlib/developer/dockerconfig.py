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
import platform
from gtmlib.common.console import ask_question
import shutil


class DockerConfig(object):
    """Class to manage configuring docker and the docker container for dev
    """
    def __init__(self):
        self.resources_root = os.path.join(resource_filename("gtmlib", "resources"), 'developer_resources')
        self.compose_file_root = os.path.join(self.resources_root, 'docker_compose')
        self.gtm_root, _, _ = resource_filename("gtmlib", "resources").rsplit(os.sep, 2)

    @staticmethod
    def prompt_with_default(question: str, default: str) -> str:
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

    def update_template_data(self, is_windows: bool, use_pycharm: bool, working_dir: str, uid: str) -> str:
        """Method to select a docker-compose template and update variables

        Args:
            is_windows:
            use_pycharm:
            working_dir:
            uid:

        Returns:

        """
        if is_windows:
            if use_pycharm:
                template_file = os.path.join(self.compose_file_root, 'pycharm-windows.yml')
            else:
                template_file = os.path.join(self.compose_file_root, 'shell-windows.yml')
        else:
            if use_pycharm:
                template_file = os.path.join(self.compose_file_root, 'pycharm-nix.yml')
            else:
                template_file = os.path.join(self.compose_file_root, 'shell-nix.yml')

        # Load template
        with open(template_file, 'rt') as template:
            data = template.read()

        # Replace values
        data = data.replace('{% WORKING_DIR %}', working_dir)

        if not is_windows:
            data = data.replace('{% USER_ID %}', str(uid))

        if not use_pycharm:
            data = data.replace('{% GTM_DIR %}', self.gtm_root)

        return data

    def write_helper_script(self, working_dir: str):
        """Write a helper script for shell developers

        Args:
            working_dir(str): Labmanager working directory

        Returns:
            None
        """
        with open(os.path.join(self.gtm_root, 'setup.sh'), 'wt') as template:
            script = """#!/bin/bash
            export HOST_WORK_DIR={}
            export PYTHONPATH=$PYTHONPATH:/opt/project/gtmlib/resources/submodules/labmanager-common
            cd /opt/project/gtmlib/resources/submodules
            su giguser
            """.format(working_dir)

            template.write(script)

    def configure(self) -> None:
        """Method to configure gtm for building and using dev containers

        Returns:
            None
        """
        # Check if *nix or windows
        if platform.system() == 'Windows':
            is_windows = True
        else:
            is_windows = False

        # Check if doing frontend or backend dev
        is_backend = ask_question("I want to configure gtm for BACKEND development")
        use_pycharm = False
        import_run_configs = False
        if is_backend:
            # If backend, check if using pycharm
            use_pycharm = ask_question("I want to use PYCHARM for development")
            if use_pycharm:
                # If using pycharm, check if user wants to import run configurations
                import_run_configs = ask_question("I want to import run configurations into my `gtm` PyCharm project")

        # Prompt for working dir
        working_dir = self.prompt_with_default("LabManager Working Directory",
                                               os.path.expanduser(os.path.join("~", 'gigantum')))

        # Prompt for UID if needed
        uid = None
        if not is_windows:
            # Set user id
            uid = self.prompt_with_default("Desired User ID", os.getuid())

        # Get template text and update with variables
        template_data = self.update_template_data(is_windows, use_pycharm, working_dir, uid)

        # Generate docker-compose file
        output_file = os.path.join(self.resources_root, 'docker-compose.yml')
        with open(output_file, 'wt') as out_file:
            out_file.write(template_data)

        print("Docker Compose file written to {}".format(output_file))

        # Generate supervisord.conf
        if is_backend:
            supervisord_file = os.path.join(self.resources_root, 'supervisord_backend.conf')

            if not use_pycharm:
                # Write shell helper script
                self.write_helper_script(working_dir)
        else:
            supervisord_file = os.path.join(self.resources_root, 'supervisord_frontend.conf')

        shutil.copyfile(supervisord_file, os.path.join(self.resources_root, 'supervisord.conf'))

        # Import run configs if needed
        if import_run_configs:
            src_run_config_dir = os.path.join(self.resources_root, 'pycharm_run_configurations')
            run_config_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.idea', 'runConfiguraions')

            files = os.listdir(src_run_config_dir)
            for file in files:
                file = os.path.join(src_run_config_dir, file)
                if os.path.isfile(file):
                    shutil.copy(file, run_config_dir)

            print("Run configurations copied to `.idea/runConfiguration`. Restart PyCharm if running")
