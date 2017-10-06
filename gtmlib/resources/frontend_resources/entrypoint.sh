#!/bin/bash

# Add local user
# Either use the LOCAL_USER_ID if passed in at runtime or
# fallback

#if [ -z "$WINDOWS_HOST" ]; then
#
#    USER_ID=${LOCAL_USER_ID:-9001}
#
#    echo "Starting with UID : $USER_ID"
#    useradd --shell /bin/bash -u $USER_ID -o -c "" -m giguser
#    export HOME=/home/giguser
#
#    # Allow user to write to the build dir with the proper permissions
#    chown giguser:root /opt/labmanager-ui
#    cd /opt/labmanager-ui/
#    chown giguser:root -R $(ls | awk '{if($1 != "node_modules"){ print $1 }}')
#
#    exec gosu giguser "$@"
#
#else
    exec "$@"
#fi
