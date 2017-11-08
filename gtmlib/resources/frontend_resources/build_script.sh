#!/usr/bin/env bash

set -e

# Copy source to build location
cp -R /mnt/labmanager-ui/* /opt/build_dir
#cd /opt/build_dir/
#chown giguser:root -R $(ls | awk '{if($1 != "node_modules"){ print $1 }}')

# Update node
cd /opt/build_dir
yarn install

# Run relay
yarn relay

# Run build
yarn build

# Copy build dir to share
mkdir /mnt/labmanager-ui/build/
cp -R /opt/build_dir/build/* /mnt/labmanager-ui/build/
