FROM ubuntu:16.04
MAINTAINER Gigantum <hello@gigantum.io>

# Install system level dependencies
RUN apt-get -y update; apt-get -y upgrade
RUN apt-get -y install python3-dev python3-pip libleveldb-dev libleveldb1v5 git nginx

# Setup Global git config
RUN git config --global user.email "noreply@gigantum.io"; git config --global user.name "Gigantum AutoCommit"

# Copy LabManager Software
RUN mkdir /opt/labmanager-common; mkdir /opt/labmanager-service-labbook; mkdir /opt/labmanager-ui
COPY ../../../components/labmanager-common /opt/labmanger-common

# Install python environment
#RUN pip3 install -U pip

# Setup NGINX/uWSGI
#COPY nginx.conf /etc/nginx/conf.d/

# Expose Ports


#