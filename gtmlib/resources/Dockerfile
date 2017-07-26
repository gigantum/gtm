FROM ubuntu:16.04
MAINTAINER Gigantum <hello@gigantum.io>

# Install system level dependencies
RUN apt-get -y update; apt-get -y upgrade
RUN apt-get -y install python3-dev python3-pip libleveldb-dev libleveldb1v5 git nginx supervisor

# Setup Global git config
RUN git config --global user.email "noreply@gigantum.io"; git config --global user.name "Gigantum AutoCommit"

# Copy LabManager Software
COPY submodules/labmanager-common /opt/labmanager-common
COPY submodules/labmanager-service-labbook /opt/labmanager-service-labbook
COPY submodules/labmanager-ui /opt/labmanager-ui

# Install lmcommon
RUN cd /opt/labmanager-common/; python3 setup.py install

# Setup lmcommon config file - should be written by automation before copy
COPY labmanager-config.yaml /etc/gigantum/labmanager.yaml

# Install API deps
RUN pip3 install -r /opt/labmanager-service-labbook/requirements.txt
RUN pip3 install uwsgi
RUN mkdir -p /mnt/gigantum

# Setup NGINX/uWSGI
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
#COPY uwsgi.ini /opt/labmanager-service-labbook
COPY nginx.conf /etc/nginx/sites-enabled/

# Expose Ports
EXPOSE 3000
#EXPOSE 8888

# Typically start by firing up uwsgi+nginx, but use CMD so it's easy to override
CMD ["/usr/bin/supervisord", "--nodaemon"]