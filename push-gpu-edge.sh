#!/bin/bash

set -e

GREEN='\033[0;32m'
NC='\033[0m'


if [ "$1" = "-h" ]; then
  echo "Pushes latest build of labmanager to gigantum/gpu-edge on Dockerhub"
  exit 0
fi

if [ -z $1 ]; then
  imageid=$(docker images | grep "gigantum.labmanager " | grep latest | awk '{ print $3 }')
  if [ -z $imageid ]; then
  	echo "** ERROR - Docker image $imageid not found"
	exit 1
  fi
  when=$(docker images | grep "gigantum.labmanager " | grep latest | awk '{ print($4 " " $5 " " $6) }')
  echo -e "Using autodetected image id $GREEN$imageid$NC (built $when)\n"
else
  imageid=$1
  echo "Using docker image id $imageid ..."
  imgs="$(docker images | grep $imageid)"
  if [ -z $imgs ]; then
  	echo "** ERROR - Docker image $imageid not found"
	exit 1
  fi
fi

echo -e "Adding 'gigantum/gpu-edge' tag to given docker image $imageid...\n"
docker tag $imageid gigantum/gpu-edge:latest
echo "$(docker images | head -n 1)"
echo -e "$GREEN$(docker images | head | grep gigantum.gpu-edge | grep latest)$NC"

echo -ne "\nConfirm push $imageid gigantum/gpu-edge to hub.docker.com (y/n)? "
read answer
if [ "$answer" = "y" ]; then
	docker push gigantum/gpu-edge
else
	echo "NOT pushing to hub.docker.com"
fi
