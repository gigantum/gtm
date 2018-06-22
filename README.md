# gtm

A command line interface tool for managing the Gigantum client application and
library for development, testing, and deployment.

If you are simply interested in *using* Gigantum, please follow our [download
instructions](https://gigantum.com/download) and visit the user docs at
[http://docs.gigantum.com](http://docs.gigantum.com).

This repository contains submodules that comprise the complete gigantum
application, which is intended to run as a [Docker
container](https://www.docker.com/what-container).

Tooling is included to ease setup of
[PyCharm](https://www.jetbrains.com/pycharm/) for remote Docker debugging.

Below are rough and ready instructions on how to develop on the application.
Further information is provided in the `docs/` directory. In particular, if you
are interested in contributing back to the Gigantum codebase (gtm or it's
submodules), please read `docs/contributing.md`.

## Installation

`gtm` is Python3 only, and has a few dependencies that must be installed. Its
recommended that you create a virtualenv to install `gtm`.

1. Install Docker

   The `gtm` tool requires Docker on your host machine to build and launch
   images. Follow Docker's instructions for your OS.

2. Install Python 3

   If your OS does not already have Python3 installed, you'll have to install
   it. For example:

   OSX
   ```
   $ brew install python3
   ```

   Windows
   ```
   PS> choco install python3
   ```

3. Create a virtualenv (strongly recommended)

   Using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/):

   ```
   $ mkvirtualenv --python=python3 gtm
   ```

   Alternatively, if you are using Anaconda or Miniconda, you could use:

   ```
   $ conda create -n gtm python=3
   ```

4. Clone the `gtm` repository
([https://github.com/gigantum/gtm](https://github.com/gigantum/gtm))

   - `master` branch will be the last public release
   - `integration` branch will be the latest working updates

5. Initialize submodules

   All of the components of the gigantum system are linked into this
   repository via submodules. You'll need to initialize them before use

   ```
   $ cd gtm
   $ git submodule update --init --recursive
   ```

6. Install the python dependencies into your virtualenv:

   ```
   $ workon gtm  # if using virtualenvwrapper
   $ pip install -r requirements.txt
   ```

## Contents

The `gtm` repo contents:

 `/bin` - [FUTURE] useful scripts for the developer

 `/docs` - [FUTURE] developer documentation and notes

 `/gtmlib` - The Python package containing the gtm CLI internals

 `/gtmlib/common` - Subpackage for `gtm` functionality common across components

 `/gtmlib/labmanager` - Subpackage for functionality related to building the
 "production" app container

 `/gtmlib/developer` - Subpackage for functionality related to building the
 "developer" app container

 `/gtmlib/circleci` - Subpackage for functionality related to building
 containers for CircleCI

 `/gtmlib/baseimage` - Subpackage for functionality related to building
 gigantum bases

 `/gtmlib/resources` - Location for all build resources. This is where external
 repos are included as submodule refs

 `/gtmlib/tests` - `gtm` tool tests

 `/gtm.py` - The CLI python script


## Usage

The `gtm` tool is available via a python command line interface with future installation as a system level script.

Use ```python gtm.py -h``` to print the help contents for the tool.

The basic command structure is:

```
python gtm.py <optional args> <component> <command>
```

Where the supported system **components** are:

- **labmanager** - the client application for interacting with Gigantum LabBooks
- **developer** - tooling for building and using developer containers
- **base-image** - tooling for building and publishing Base Images maintained by Gigantum
- **circleci** - tooling for building and publishing CircleCI images

Each system component can have different supported commands based on the actions that are available. They are summarized
below:

- **labmanager**
    - `build` - command to build the LabManager Docker image. The build process
      will use the current submodule references, so if you want build a
      different version of the code (e.g. you're developing on a feature
      branch), update the submodules refs before running this command.

      You can provide a name for the image using the `--override-name`
      argument. If omitted the image will automatically be named using the
      commit hash of the `gtm` repo.

      This operation will first build a container to compile the React based
      frontend. It will then use this container to compile the frontend.
      Finally, the LabManager container will be built.

    - `start` - start the LabManager container. If you omit `--override-name`
      the image name be automatically generated using the commit hash of the
      `gtm` repo. This operation will mount your working directory, Docker
      socket, and set the UID inside the container.
    - `stop` - stop the LabManager container. If you omit `--override-name` the
      image name be automatically generated using the commit hash of the `gtm`
      repo.
    - `test` - run all tests in the LabManager container.

- **developer**
    - `setup` - Configure your `gtm` repository for developer container use.

      This command will walk you through setting up your environment for
      backend or frontend dev and shell or PyCharm based dev.  If using
      PyCharm, [checkout the detailed setup documentation
      here](docs/pycharm-dev.md).

      Practically, this command will configure the entrypoint.sh,
      supervisor.conf, and docker-compose.yml files for you. If you want to
      change configurations it is safe to re-run.

      When in "frontend" dev mode, the API will start up automatically at
      [localhost:5000](http://localhost:5000). You will need to run `npm run
      start` manually (after attaching) if you want to start the dev server.

      When in "backend" dev mode, the frontend will automatically be hosted at
      [localhost:3000](http://localhost:3000).  You will need to run `python3.6
      service.py` manually if you want to start the API.

    - `build` - Build the development container.

      This command runs a similar build process as the primary `gtm labmanager
      build` command, but it does not actually install the software and
      configures things slightly different.

      Since the submodule directory is shared (either explicitly or
      automatically in the case of PyCharm) you do not need to rebuild the dev
      container unless a dependency changes. All code changes will mirror
      automatically.

      **Note:** this command installs all the node packages locally in the
      `labmanager-ui` submodule so the dev server can run.  This is a huge
      directory with lots of tiny files. To deal with IO issues, the command
      will install the packages locally, zip them up, copy back to the share,
      and unzip. You only need to "re-install" the packages if the UI repo
      changes. Otherwise, gtm will manage this directory for you so docker
      still builds quickly.

    - `run` - Start the dev container via docker-compose.

      If you are using PyCharm, you should not need this command. PyCharm will
      automatically start/stop containers as needed. It also automatically
      mounts the code.

      If you are using shell-based dev, run this command to fire up the dev
      container. The `gtm/gtmlib/resources/submodules` directory will
      automatically mount to `/opt/project` with the correct permissions. *The
      service must then be run manually (see `attach` sub-command below).

    - `attach` - Drop into a shell in the running dev container (using docker
      exec).

      This command will start a shell inside the running dev container as root.
      Run `cd /opt/project` to drop into the mounted code directory.

      Suggested method for running the API while developing in backend
      configuration:

      ```
      $ cd /opt/project
      $ source setup.sh
      $ cd labmanager-service-labbook
      $ python3.6 service.py
      ```

      `setup.sh` will setup environment variables, cd to the submodules
      directory, and switch to `giguser` so the API is running in the correct
      context

      Suggested method for running the dev node server while developing in
      frontend configuration:

      ```
      #todo
      ```

      You can run multiple `gtm developer attach` commands in multiple terminal
      windows if desired.

    - `relay` - Run `relay-compiler` to re-generate relay queries. A
      convienence method for frontend development.  The `build` command runs
      this command at the end of the build process automatically.


- **base-image**  
  *Publishing is currently necessary in order for the Gigantum application to
  use a base-image. Please submit an issue if you're interested in developing a
  base-image.*

    - `build` - command to build the Gigantum maintained images. Will
      automatically tag with a unique tag based on the current `gtm` repo
      commit hash and the date (useful for doing regular security updates, but
      not really changing much).

      You can provide a name for a single image to build using the
      `--override-name` argument. If omitted the image will automatically build
      all available images. Images Dockerfile definitions are stored in
      [https://github.com/gigantum/base-images](https://github.com/gigantum/base-images)

    - `publish` - command to publish built images to hub.docker.com. This
      command will reference a tracking file and only publish images that have
      been previously built, but not yet published. NOTE: this will only
      succeed if you have permission to publish to the target Docker Hub
      organization (currently hard-coded to gigantum). 

- **circleci**
  When you update a dependency (e.g. edit the requirements.txt file) in one
  of the core app repositories you need to rebuild the container for tests to
  pass on circle. You should do this and include the changes to circleci
  config in your PR, so when merged tests continue to pass.

    - `build-common` - command to build the docker image for CircleCI when
      testing the `lmcommon` repository. This method will build and push a new
      image to DockerHub. The resulting "organization/repo:tag" string that is
      printed should be pasted into the circleCI config file in the `lmcommon`
      repo to update. Commit and push and CircleCI will use the new image.

    - `build-api` - command to build the docker image for CircleCI when
      testing the `labmanager-service-labbook` repository. This method will
      build and push a new image to DockerHub. The resulting
      "organization/repo:tag" string that is printed should be pasted into the
      circleCI config file in the `labmanager-service-labbook` repo to update.
      Commit and push and CircleCI will use the new image.


## Testing

The `gtm` tool itself has unit tests written in pytest. To run them, simply
execute pytest

```
$ workon gtm  # assuming you're using virtualenvwrapper!
$ cd gtm
$ pytest
```
