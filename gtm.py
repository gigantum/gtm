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
import argparse
import os
import sys

from gtmlib import labmanager


def format_action_help(actions):
    """Method to format a help string for actions in a component

    Args:
        actions(list): list of supported actions

    Returns:
        str
    """
    response = ""
    for action in actions:
        response = "{}      {}: {}".format(response, action[0], action[1])

    return response


def format_component_help(components):
    """Method to format a help string for all the components

    Args:
        components(dict): Dictionary of supported components

    Returns:
        str
    """
    response = ""
    for component in components:
        response = "{}  {}\n{}".format(response, component, format_action_help(components[component]))

    return response


def labmanager_actions(args):
    """Method to provide logic and perform actions for the LabManager component

    Args:
        args(Namespace): Parsed arguments

    Returns:
        None
    """
    builder = labmanager.LabManagerBuilder()

    if "override_name" in args:
        if args.override_name:
            builder.image_name = args.override_name

    if args.action == "build":
        if "name" in args:
            if args.name:
                builder.image_name = args.override_name

        builder.build_image(show_output=args.verbose)

        # Print Name of image
        print("\n\n\n*** Built LabManager Image: {}".format(builder.image_name))
    elif args.action == "start" or args.action == "stop":
        launcher = labmanager.LabManagerRunner(image_name=builder.image_name, container_name=builder.container_name,
                                               show_output=args.verbose)

        if args.action == "start":
            if not launcher.is_running:
                launcher.launch()
                print("*** Ran: {}".format(builder.image_name))
            else:
                print("Error: Docker container by name `{}' is already started.".format(builder.image_name), file=sys.stderr)
                sys.exit(1)
        elif args.action == "stop":
            if launcher.is_running:
                launcher.stop()
                print("*** Stopped: {}".format(builder.image_name))
            else:
                print("Error: Docker container by name `{}' is not started.".format(builder.image_name), file=sys.stderr)
                sys.exit(1)
    elif args.action == "test":
        tester = labmanager.LabManagerTester(builder.container_name)
        tester.test()
    else:
        print("Error: No action provided.", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    # Setup supported components and commands
    components = {}
    components['labmanager'] = [["build", "Build the LabManager Docker image"],
                                ["start", "Start a Lab Manager Docker image"],
                                ["stop", "Stop a LabManager Docker image"],
                                ["test", "Run internal tests on a LabManager Docker image"]]

    # Prep the help string
    help_str = format_component_help(components)
    component_str = ", ".join(list(components.keys()))

    description_str = "Developer command line tool for the Gigantum platform. "
    description_str = description_str + "The following components and actions are supported:\n\n{}".format(help_str)

    parser = argparse.ArgumentParser(description=description_str,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--override-name", "-n",
                        default=None,
                        metavar="<name>",
                        help="String to use as the image name")
    parser.add_argument("--verbose", "-v",
                        default=False,
                        action='store_true',
                        help="Boolean indicating if detail status should be printed")
    parser.add_argument("--no-cache",
                        default=False,
                        action='store_true',
                        help="Boolean indicating if docker cache should be ignored")
    parser.add_argument("component",
                        choices=list(components.keys()),
                        metavar="component",
                        help="System to interact with. Supported components: {}".format(component_str))
    parser.add_argument("action", help="Action to perform on a component")

    args = parser.parse_args()

    if args.component == "labmanager":
        # LabManager Selected
        labmanager_actions(args)
