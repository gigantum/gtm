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

# Setup everything to allow giguser to run nginx and git
chown -R giguser:root /opt/
chown giguser:root /run/docker.sock
chmod 777 /var/run/docker.sock
cp /root/.gitconfig /home/giguser/

# symlink the pre-compiled application into the code repo so it runs
mkdir /mnt/repos/labmanager-ui/build
ln -s /var/www /mnt/repos/labmanager-ui/build

# Start supervisord
/usr/bin/supervisord &

exec gosu giguser "$@"
