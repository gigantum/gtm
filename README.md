# gtm
A command line interface tool for managing the Gigantum LabManager and Library development, testing, and deployment.


## Installation

`gtm` is Python3 only, and has a few dependencies that must be installed. Its recommended that you create a virtualenv
to install `gtm`.

1. Install Docker

    The `gtm` tool requires Docker on your host machine to build and launch images. Follow Docker's instructions for your
    OS.

2. Install Python 3
    
    If your OS does not already have Python3 installed, you'll have to install it.
    
    OSX
    ```
    brew install python3
    ```
    
    Windows
    ```
    #TODO
    ```
    
3. Create a virtualenv

	Using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/):
	
	```
	mkvirtualenv --python=python3 gtm
	```
	
3. Clone the `gtm` repository
([https://github.com/gigantum/gtm](https://github.com/gigantum/gtm))
    
    - `master` branch will be the last release
    - `integration` branch will be the latest working updates
    
4. Initialize submodules
    
    All of the components of the gigantum system are linked into this repository via submodules. You'll need to initialize
them before use

    ```
    cd gtm
    git submodule update --init --recursive    
    ```
 
5. Install the python dependencies into your virtualenv:

    ```
    workon gtm
    pip install -r requirements.txt
    ```

## Contents

The `gtm` repo contents:
 
 `/bin` - [FUTURE] useful scripts for the developer
 
 `/docs` - [FUTURE] developer documentation and notes

 `/gtmlib` - The Python package containing the gtm CLI internals
    
 `/gtmlib/common` - Subpackage for `gtm` functionality common across components
 
 `/gtmlib/labmanager` - Subpackage for functionality related to the LabManager application
 
 `/gtmlib/resources` - Location for all build resources. This is where external repos are included as submodule refs
 
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
    
Each system component can have different supported commands based on the actions that are available. They are summarized
below:

- **labmanager** 
    - `build` - command to build the LabManager Docker image. The build process will use the current submodule
     references, so if you want build a different version of the code (e.g. you're developing on a feature branch),
     update the submodules refs before running this command. 
     
        You can provide a name for the image using the `--override-name` argument. If omitted
    the image will automatically be named using the commit hash of the `gtm` repo.
    
        This operation will first build a container to compile the React based frontend. It will then use this container
        to compile the frontend. Finally, the LabManager container will be built.
    
    - `start` - start the LabManager container. If you omit `--override-name` the image name be automatically
     generated using the commit hash of the `gtm` repo. This operation will mount your working directory, Docker socket,
     and set the UID inside the container
    - `stop` - stop the LabManager container. If you omit `--override-name` the image name be automatically
     generated using the commit hash of the `gtm` repo. 
    - `test` - run all tests in the LabManager container.
    
- **developer** 
    - `setup` - Configure your `gtm` repository for developer container use. 
    
        This command will walk you through setting up your environment for backend or frontend dev and shell or PyCharm based dev. 
        If using PyCharm, [checkout the detailed setup documentation here](docs/pycharm-dev.md). 
    
        Practically, this command will configure the entrypoint.sh, supervisor.conf, and docker-compose.yml files 
        for you. If you want to change configurations it is safe to re-run.
        
        When in "frontend" dev mode, the API will start up automatically at [localhost:5000](http://localhost:5000). You
        will need to run `npm run start` manually (after attaching) if you want to start the dev server.
        
        When in "backend" dev mode, the frontend will automatically be hosted at [localhost:3000](http://localhost:3000).
        You will need to run `python3.6 service.py` manually if you want to start the API.
    
    - `build` - Build the development container. 
    
        This command runs a similar build process as the primary
        `gtm labmanager build` command, but it does not actually install the software and configures things slightly different.
    
        Since the submodule directory is shared (either explicitly or automatically in the case of PyCharm) you do not
        need to rebuild the dev container unless a dependency changes. All code changes will mirror automatically.
        
        **Note:** this command installs all the node packages locally in the `labmanager-ui` submodule so the dev server can run.
        This is a huge directory with lots of tiny files. To deal with IO issues, the command will install the packages
        locally, zip them up, copy back to the share, and unzip. You only need to "re-install" the packages if the 
        UI repo changes. Otherwise, gtm will manage this directory for you so docker still builds quickly.
     
    - `run` - Start the dev container via docker-compose.
        
        If you are using PyCharm, you should not need this command. PyCharm will automatically start/stop containers
        as needed. It also automatically mounts the code.
        
        If you are using shell-based dev, run this command to fire up the dev container. The `gtm/gtmlib/resources/submodules`
        directory will automatically mount to `/opt/project` with the correct permissions.
     
    - `attach` - Drop into a shell in the running dev container. 
    
        This command will start a shell inside the running dev container as root. Run `cd /opt/project` to drop into the
        mounted code directory. 
        
        Suggested method for running the API while developing in backend configuration:
        
        ```
        cd /opt/project
        source setup.sh
        cd labmanager-service-labbook
        python3.6 service.py
        ```
        
        `setup.sh` will setup environment variables, cd to the submodules directory, and switch to `giguser` so the API
        is running in the correct context   
        
        Suggested method for running the dev node server while developing in frontend configuration:
        
        ```
        #todo
        ```     
        
        You can run multiple `gtm developer attach` commands in multiple terminal windows if desired.
    
- **base-image** 
    - `build` - command to build the Gigantum maintained images. Will automatically tag with a unique tag based on the 
    current `gtm` repo commit hash and the date (useful for doing regular security updates, but not really changing
    much).
    
        You can provide a name for a single image to build using the `--override-name` argument. If omitted
    the image will automatically build all available images. Images Dockerfile definitions are stored in
    [https://github.com/gigantum/base-images](https://github.com/gigantum/base-images)
    
    - `publish` - command to publish built images to hub.docker.com. This command will reference a tracking file and
    only publish images that have been previously built, but not yet published.
    
        *Note: Currently images are pushing to `gtmdev` organization on hub.docker.com. You must be in this org to push
        in the future we'll push to our proper organization*


## Testing

The `gtm` tool itself has unit tests written in pytest. To run them, simply execute pytest

```
workon gtm
cd gtm
pytest
```