#!/bin/bash

# TODO: Generalize Dev Env Vars
export JUPYTER_RUNTIME_DIR=/mnt/share/jupyter/runtime

USER_ID=${LOCAL_USER_ID:-9001}
echo "Starting with UID : $USER_ID"
useradd --shell /bin/bash -u $USER_ID -o -c "" -m giguser
export HOME=/home/giguser

# DMK - only need to run permissions once.
# Setup permissions to allow giguser to build UI components and run git
chown -R giguser:root /opt/run
chown -R giguser:root /opt/log
chown -R giguser:root /opt/redis
chown -R giguser:root /etc/elasticsearch
chown -R giguser:root /usr/share/elasticsearch
mkdir -p /mnt/gigantum/.labmanager/elasticsearch/data
mkdir -p /mnt/gigantum/.labmanager/elasticsearch/logs
chown -R giguser:root /mnt/gigantum/.labmanager/elasticsearch

# TODO: Remove once package introspection occurs in target container
chown -R giguser:root /opt/conda/pkgs/cache

# Setup git config for giguser
gosu giguser bash -c "git config --global user.email 'noreply@gigantum.io'"
gosu giguser bash -c "git config --global user.name 'Gigantum AutoCommit'"
gosu giguser bash -c "git config --global credential.helper store"


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

    # Setup docker sock perms in the container
    chown giguser:root /var/run/docker.sock
    chmod 777 /var/run/docker.sock
fi

# Start supervisord
gosu giguser /usr/bin/supervisord &
exec gosu giguser "$@"
