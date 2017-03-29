#!/bin/bash

if [ "$(id -u)" != "0" ]; then
echo "This script must be run as root!" 2>&1
exit 1
fi

echo "#################################"
echo "### OTFNFV Tool Configuration ###"
echo "#################################"
echo

# Create config file in /etc
cp "otfnfv.conf.example" "/etc/otfnfv.conf"
echo "[OK] OTFNFV config file in /etc"
echo

# Move controller application to correct path
echo -n "Ryu directory path: "
read DIRECTORY

if [ -d "$DIRECTORY" ]; then
    cp "controller.py" "$DIRECTORY/ryu/app/"
    echo "[OK] Ryu controller application"
    echo
else
    echo
    echo "Directory doesn't exist! Exiting..."
    exit 1
fi

# Create log directory
if [ ! -d "/var/log/otfnfv/" ]; then
    mkdir "/var/log/otfnfv/"
    echo "[OK] Created log directory in /var/log/"
fi

# Create UDS Socket
touch /var/run/statistics_socket
echo "[OK] UDS Socket"
echo

# Create symbolic link to executable
echo -n "Inform otfnfv source code path"
read DIRECTORY

if [ -d "$DIRECTORY" ]; then
    if [ ! -f "/bin/otfnfv" ]; then
        sudo ln -s "$DIRECTORY/src/otfnfv/otfnfv.py" "/bin/otfnfv"
        echo "[OK] Created symbolic link to executable"
    fi
else
    echo
    echo "Directory doesn't exist! Exiting..."
    exit 1
fi

echo
echo "OTFNFV Tool is configured!"
