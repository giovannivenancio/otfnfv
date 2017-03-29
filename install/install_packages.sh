#!/bin/sh

##
## Bash install script for missing packages
##

# Make sure we're running with root permissions
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

apt-get update

apt-get install -y \
    vim python-pip \
    python-webob python-routes python-oslo.config \
    python-msgpack python-eventlet python-imaging-tk

pip install \
    tinyrpc ovs Pillow \
    numpy matplotlib pymongo
