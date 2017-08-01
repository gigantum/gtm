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


## Testing

The `gtm` tool itself has unit tests written in pytest. To run them, simply execute pytest

```
workon gtm
cd gtm
pytest
```