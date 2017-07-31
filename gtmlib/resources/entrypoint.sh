#!/bin/bash

# Add local user
# Either use the LOCAL_USER_ID if passed in at runtime or
# fallback

USER_ID=${LOCAL_USER_ID:-9001}

echo "Starting with UID : $USER_ID"
useradd --shell /bin/bash -u $USER_ID -o -c "" -m giguser
export HOME=/home/giguser

# Setup everything to allow giguser to run nginx and git
chown -R giguser:root /opt/
chown -R giguser:root /var/log/nginx/
chown -R giguser:root /var/lib/nginx/
chown giguser:root /var/lock/nginx.lock
chown giguser:root /run/nginx.pid
chown giguser:root /run/docker.sock
chmod 777 /var/run/docker.sock
cp /root/.gitconfig /home/giguser/

exec gosu giguser "$@"