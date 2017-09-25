#!/bin/bash

# Add local user
# Either use the LOCAL_USER_ID if passed in at runtime or
# fallback

USER_ID=${LOCAL_USER_ID:-9001}

echo "Starting with UID : $USER_ID"
useradd --shell /bin/bash -u $USER_ID -o -c "" -m giguser
export HOME=/home/giguser

# BVB - Required to get rq to run.
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# TODO: Generalize Dev Env Vars
export JUPYTER_RUNTIME_DIR=/mnt/share/jupyter/runtime

# Set permissions for container-container share
chown -R giguser:root /mnt/share/

# Setup everything to allow giguser to run nginx and git
chown -R giguser:root /opt/log
chown -R giguser:root /opt/nginx
chown -R giguser:root /opt/redis
chown -R giguser:root /opt/run
chown -R giguser:root /var/lib/nginx/
chown -R giguser:root /var/log/nginx/
chown giguser:root /var/lock/nginx.lock
chown giguser:root /run/nginx.pid
chown giguser:root /var/run/docker.sock
chmod 777 /var/run/docker.sock
cp /root/.gitconfig /home/giguser/

if [ -z "$WINDOWS_HOST" ]; then
    # Not a windows host
    exec gosu giguser "$@"
else
    # A windows host
    exec "$@"
fi

