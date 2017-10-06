#!/bin/bash

# BVB - Required to get rq to run.
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# Setup python path
export PYTHONPATH=$PYTHONPATH:/opt/project/gtmlib/resources/submodules/labmanager-common

# TODO: Generalize Dev Env Vars
export JUPYTER_RUNTIME_DIR=/mnt/share/jupyter/runtime

# If not on a windows host, create user to match host user's UID and setup permissions on shares
if [ -z "$WINDOWS_HOST" ]; then
    USER_ID=${LOCAL_USER_ID:-9001}
    echo "Starting with UID : $USER_ID"
    useradd --shell /bin/bash -u $USER_ID -o -c "" -m giguser
    export HOME=/home/giguser

    # DMK - only need to run permissions once.
    # Setup permissions to allow giguser to build UI components and run git
    chown -R giguser:root /opt/run
    chown -R giguser:root /opt/log
    chown -R giguser:root /opt/redis
    cp /root/.gitconfig /home/giguser/

fi

if [ -n "$SET_PERMISSIONS" ]; then
    # This is a *nix config running shell dev so you need to setup perms on the mounted code (skipping node packages)
   cd $SET_PERMISSIONS
   chown giguser:root -R labmanager-common
   chown giguser:root -R labmanager-service-labbook
   cd $SET_PERMISSIONS/labmanager-ui
   chown giguser:root -R $(ls | awk '{if($1 != "node_modules"){ print $1 }}')
fi

if [ -n "$NPM_INSTALL" ]; then
    # Building relay so fix permissions and ignore share dir since not in operating mode
   chown -R giguser:root /mnt/node_build
   chown giguser:root /mnt/src
   cd /mnt/src
   chown giguser:root -R $(ls | awk '{if($1 != "node_modules"){ print $1 }}')
else
    # If here, in "operational mode", not building or configuring
    # Set permissions for container-container share
    chown -R giguser:root /mnt/share/

    if [ -z "$WINDOWS_HOST" ]; then
        # Setup docker sock perms in the container
        chown giguser:root /var/run/docker.sock
        chmod 777 /var/run/docker.sock
    fi
fi

# Start supervisord
gosu giguser /usr/bin/supervisord &

# su to giguser if not on Windows
if [ -z "$WINDOWS_HOST" ]; then
    # Not a windows host
    exec gosu giguser "$@"
else
    # A windows host
    exec "$@"
fi
