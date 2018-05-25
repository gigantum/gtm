#!/bin/bash

# BVB - Required to get rq to run.
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# TODO: Generalize Dev Env Vars
export JUPYTER_RUNTIME_DIR=/mnt/share/jupyter/runtime

# Open up the docker socket for now
chmod 777 /var/run/docker.sock

# Add local user
# Either use the LOCAL_USER_ID if passed in at runtime or
# fallback
USER_ID=${LOCAL_USER_ID:-9001}

echo "Starting with UID: $USER_ID"
useradd --shell /bin/bash -u $USER_ID -o -c "" -m giguser
export HOME=/home/giguser

# Set permissions for container-container share
chown -R giguser:root /mnt/share/

# Set permissions for demo labbook
chown giguser:root /opt/awful-intersections-demo_2018-03-14.lbk

# Setup git config for giguser
gosu giguser bash -c "git config --global user.email 'noreply@gigantum.io'"
gosu giguser bash -c "git config --global user.name 'Gigantum AutoCommit'"
gosu giguser bash -c "git config --global credential.helper store"

# Setup everything to allow giguser to run nginx and git
chown -R giguser:root /opt/log
chown -R giguser:root /opt/nginx
chown -R giguser:root /opt/redis
chown -R giguser:root /opt/run
chown -R giguser:root /opt/labmanager-common
chown -R giguser:root /opt/labmanager-service-labbook
chown -R giguser:root /var/lib/nginx/
chown -R giguser:root /var/log/nginx/
chown --silent giguser:root /var/lock/nginx.lock
chown giguser:root /run/nginx.pid
chown giguser:root /var/run/docker.sock

gosu giguser git lfs install
exec gosu giguser "$@"

