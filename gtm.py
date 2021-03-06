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
from gtmlib import developer
from gtmlib import baseimage
from gtmlib import circleci
from gtmlib.common.logreader import show_log


def format_action_help(actions):
    """Method to format a help string for actions in a component

    Args:
        actions(list): list of supported actions

    Returns:
        str
    """
    response = ""
    for action in actions:
        response = "{}      {}: {}\n".format(response, action[0], action[1])

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
        builder.build_image(show_output=args.verbose, no_cache=args.no_cache)

        # Print Name of image
        print("\n\n*** Built LabManager Image: {}\n".format(builder.image_name))

    elif args.action == "publish":
        image_tag = None

        builder.publish(image_tag=image_tag, verbose=args.verbose)

        # Print Name of image
        if not image_tag:
            image_tag = "latest"
        print("\n\n*** Published LabManager Image: gigantum/labmanager:{}\n".format(image_tag))

    elif args.action == "publish-edge":
        image_tag = None
        if "override_name" in args:
            if args.override_name:
                image_tag = args.override_name

        builder.publish_edge(image_tag=image_tag, verbose=args.verbose)

        # Print Name of image
        if not image_tag:
            image_tag = "latest"
        print("\n\n*** Published LabManager-Edge Image: gigantum/labmanager-edge:{}\n".format(image_tag))

    elif args.action == "publish-demo":
        image_tag = None
        if "override_name" in args:
            if args.override_name:
                image_tag = args.override_name

        builder.publish_demo(image_tag=image_tag, verbose=args.verbose)

        # Print Name of image
        if not image_tag:
            image_tag = "latest"
        print("\n\n*** Published Demo Image: gigantum/gigantum-cloud-demo:{}\n".format(image_tag))
    elif args.action == "prune":
        builder.cleanup(dev_images=False)

    elif args.action == "run":
        print("Error: Unsupported action provided: `{}`. Did you mean `start`?".format(args.action), file=sys.stderr)
        sys.exit(1)
    elif args.action == "log":
        show_log()
    elif args.action == "start" or args.action == "stop":
        # If not a tagged version, force to latest
        if ":" not in builder.image_name:
            image_name = "{}:latest".format(builder.image_name)
        else:
            image_name = builder.image_name

        launcher = labmanager.LabManagerRunner(image_name=image_name, container_name=builder.container_name,
                                               show_output=args.verbose)

        if args.action == "start":
            if not launcher.is_running:
                launcher.launch()
                print("*** Ran: {}".format(image_name))
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
        print("Error: Unsupported action provided: `{}`".format(args.action), file=sys.stderr)
        sys.exit(1)


def demo_actions(args):
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
        builder.build_image(show_output=args.verbose, no_cache=args.no_cache, demo=True)

        # Print Name of image
        print("\n\n*** Built LabManager Image with Demo configuration: {}\n".format(builder.image_name))

    elif args.action == "publish":
        image_tag = None
        if "override_name" in args:
            if args.override_name:
                image_tag = args.override_name

        builder.publish_demo(image_tag=image_tag, verbose=args.verbose)

        # Print Name of image
        if not image_tag:
            image_tag = "latest"
        print("\n\n*** Published Demo Image: gigantum/gigantum-cloud-demo:{}\n".format(image_tag))

    else:
        print("Error: Unsupported action provided: `{}`".format(args.action), file=sys.stderr)
        sys.exit(1)


def developer_actions(args):
    """Method to provide logic and perform actions for the developer component

    Args:
        args(Namespace): Parsed arguments

    Returns:
        None
    """
    if args.action == "build":
        builder = developer.LabManagerDevBuilder()
        if "override_name" in args:
            if args.override_name:
                builder.image_name = args.override_name

        builder.build_image(show_output=args.verbose, no_cache=args.no_cache)

        # Print Name of image
        print("\n\n*** Built LabManager Dev Image: {}\n".format(builder.image_name))

    elif args.action == "prune":
        lm_builder = labmanager.LabManagerBuilder()
        lm_builder.cleanup(dev_images=True)
    elif args.action == "setup":
        dc = developer.DockerConfig()
        dc.configure()
    elif args.action == "run":
        du = developer.DockerUtil()
        du.run()
    elif args.action == "relay":
        builder = developer.LabManagerDevBuilder()
        builder.run_relay()
    elif args.action == "attach":
        du = developer.DockerUtil()
        du.attach()
    elif args.action == "log":
        show_log()
    else:
        print("Error: Unsupported action provided: {}".format(args.action), file=sys.stderr)
        sys.exit(1)


def baseimage_actions(args):
    """Method to provide logic and perform actions for the base-image component

    Args:
        args(Namespace): Parsed arguments

    Returns:
        None
    """
    builder = baseimage.BaseImageBuilder()
    image_name = None
    if ("override_name" in args) and args.override_name:
        image_name = args.override_name

    if args.action == "build":
        builder.build(image_name=image_name, verbose=args.verbose, no_cache=args.no_cache)
    elif args.action == "publish":
        builder.publish(image_name=image_name, verbose=args.verbose)

    else:
        print("Error: Unsupported action provided: {}".format(args.action), file=sys.stderr)
        sys.exit(1)


def circleci_actions(args):
    """Method to provide logic and perform actions for the circleci component

    Args:
        args(Namespace): Parsed arguments

    Returns:
        None
    """
    builder = circleci.CircleCIImageBuilder()

    if args.action == 'build-common':
        builder.build(repo_name='lmcommon', verbose=args.verbose, no_cache=args.no_cache)
    elif args.action == "build-api":
        builder.build(repo_name='labmanager-service-labbook', verbose=args.verbose)
    else:
        print("Error: Unsupported action provided: {}".format(args.action), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    # Setup supported components and commands
    components = {}
    components['labmanager'] = [["build", "Build the LabManager Docker image"],
                                ["start", "Start a Lab Manager Docker image"],
                                ["stop", "Stop a LabManager Docker image"],
                                ["test", "Run internal tests on a LabManager Docker image"],
                                ["publish", "Publish the latest build to Docker Hub"],
                                ["publish-edge", "Publish the latest build to Docker Hub as an Edge release"],
                                ["prune", "Remove all images except the latest LabManager build"],
                                ["log", "Show the client log file"],
                                ]

    components['demo'] = [["build", "Build the LabManager Docker image"],
                          ["publish", "Publish the latest build to Docker Hub as a Demo release"]]

    components['developer'] = [["setup", "Generate Docker configuration for development"],
                               ["build", "Build the LabManager Development Docker image based on `setup` config"],
                               ["relay", "Re-compile relay queries. Runs automatically on a build command."],
                               ["run", "Start the LabManager dev container (not applicable to PyCharm configs)"],
                               ["attach", "Attach to the running dev container"],
                               ["prune", "Remove all images except the latest labmanager-dev build"],
                               ["log", "Show the client log file"]]

    components['base-image'] = [["build", "Build all available base images"],
                                ["publish", "Publish all available base images to docker hub"]]

    components['circleci'] = [["build-common", "Build the CircleCI container for the `lmcommon` repo"],
                              ["build-api", "Build the CircleCI container for the `labmanager-service-labbook` repo"]]

    # Prep the help string
    help_str = format_component_help(components)
    component_str = ", ".join(list(components.keys()))

    description_str = "Developer command line tool for the Gigantum platform. "
    description_str = description_str + "The following components and actions are supported:\n\n{}".format(help_str)

    parser = argparse.ArgumentParser(description=description_str,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--override-name", "-n",
                        default=None,
                        metavar="<alternative name>",
                        help="Alternative image target for base-image or labmanager")
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
    elif args.component == "developer":
        # Base Image Selected
        developer_actions(args)
    elif args.component == "base-image":
        # Base Image Selected
        baseimage_actions(args)
    elif args.component == "circleci":
        # CircleCI Selected
        circleci_actions(args)
    elif args.component == "demo":
        demo_actions(args)
