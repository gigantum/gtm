FROM ubuntu:16.04
MAINTAINER Gigantum <hello@gigantum.io>

# Install system level dependencies
RUN apt-get -y update; apt-get -y upgrade
RUN apt-get -y install build-essential git curl autotools-dev autoconf automake python-dev

# Install node
RUN curl -sL https://deb.nodesource.com/setup_6.x | bash -
RUN apt-get -y install nodejs

# Build Watchman
RUN git clone https://github.com/facebook/watchman.git; cd watchman; git checkout v4.7.0; ./autogen.sh; ./configure; make; make install

# Copy LabManager Software
COPY submodules/labmanager-ui /opt/labmanager-ui

# Build Frontend
RUN cd /opt/labmanager-ui; npm install

# Set the react port to match nginx
ENV PORT 5000

# Copy in build script
COPY build_script.sh /opt/labmanager-ui

# Run build script on container start
CMD ["/bin/bash", "/opt/labmanager-ui/build_script.sh"]