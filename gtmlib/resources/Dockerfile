FROM ubuntu:16.04
MAINTAINER Gigantum <hello@gigantum.io>

# Install system level dependencies
RUN apt-get -y update; apt-get install -y software-properties-common; add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get -y upgrade;
RUN apt-get -y update; apt-get -y install build-essential python3.6-dev libleveldb-dev libleveldb1v5 git nginx supervisor curl gosu redis-server

# Start Redis
RUN service redis start

# Install pip with PPA 3.6 installation
RUN curl https://bootstrap.pypa.io/get-pip.py | python3.6

# Setup Global git config
RUN git config --global user.email "noreply@gigantum.io"; git config --global user.name "Gigantum AutoCommit"

# Copy LabManager Software
COPY submodules/labmanager-common /opt/labmanager-common
COPY submodules/labmanager-service-labbook /opt/labmanager-service-labbook

# Install lmcommon
RUN cd /opt/labmanager-common/; python3.6 setup.py install

# Setup lmcommon config file - should be written by automation before copy
COPY labmanager-config.yaml /etc/gigantum/labmanager.yaml

# Setup logging config file
COPY submodules/labmanager-common/lmcommon/logging/logging.json.default /etc/gigantum/logging.json

# Install API deps
RUN pip3.6 install -r /opt/labmanager-service-labbook/requirements.txt; pip3.6 install uwsgi
RUN mkdir -p /mnt/gigantum

# Copy frontend
COPY frontend_build/build/ /var/www/

# Setup NGINX/uWSGI
COPY nginx_ui.conf /etc/nginx/sites-enabled/
COPY nginx_api.conf /etc/nginx/sites-enabled/
RUN rm /etc/nginx/sites-enabled/default

# Setup Supervisord to launch both uwsgi and nginx
RUN mkdir -p /opt/log/supervisor; mkdir -p /opt/log/nginx; mkdir -p /opt/run; mkdir -p /opt/nginx; nginx; nginx -s reload; nginx -s quit
COPY supervisord_base.conf /etc/supervisor/supervisord.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod u+x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Expose Ports
EXPOSE 5000

# Start redis
CMD ["service", "redis", "start"]

# Typically start by firing up uwsgi+nginx, but use CMD so it's easy to override
CMD ["/usr/bin/supervisord", "--nodaemon"]
