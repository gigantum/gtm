gtm developer notes
===================

general gotchas
---------------

If the gigantum direcotry doesn't exist on Linux, the docker daemon will create
it on mount and it will be owned by root - thus unreadable. You can create your
gigantum directory by hand, or by using one of the more user-friendly gigantum
tools first.

base images
-----------

Base images are defined and built using descriptions in the `base-images`
submodule. The format is fairly transparent, and the easiest approach for now
is to duplicate an existing YAML file.

EVEN IF the base image is available locally, the app will look for a manifest
on Docker Hub, so you need to publish (for now) even for testing.

### Publishing

To use `base-image publish`, you need to be logged in to docker hub (can be
done from the command line with `docker login` or via the Docker for Win/Mac
GUI).  Unfortunately, Docker credentials are stored unencrypted on Linux:

    WARNING! Your password will be stored unencrypted in /home/dav/.docker/config.json.
    Configure a credential helper to remove this warning. See
    https://docs.docker.com/engine/reference/commandline/login/#credentials-store

Currently, the secretstore tar.gz packages are malformed, so just be careful?

### Informing the app

You don't have to use the app to update the base image. You can directly edit
`.gigantum/env/base/gigantum_environemtn_<labbook-name>.yaml` in the labbook's
directory.

For the UI to make an image avilable, you need to update the
environment-components repo, and if you are developing in a branch you can
specify that in `gtmlib/resources/developer_resources/labmanager-config-overrides.yaml` 
like so:

    environment:
      repo_url:
        - "https://github.com/gigantum/environment-components.git@<branch-name>"

The app will automatically update to this branch at launch (it's stored in the
.labmanager directory under your gigantum directory).