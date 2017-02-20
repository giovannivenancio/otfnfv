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
cp "otfnfv.cfg" "/etc/"
echo "[OK] Created otfnfv config file in /etc"

# Move controller application to correct location
echo -n "Inform your Ryu directory location: "
read directory
cp "controller.py" "$directory/ryu/app/"
echo "[OK] Create Ryu controller application"

# Create log dir
mkdir "/var/log/otfnfv/"
echo "[OK] Created log directory in /var/log/"

# Create UDS Socket
touch /var/run/statistics_socket
echo "[OK] Create UDS Socket"

# Create symbolic link to executable
echo -n "Inform otfnfv executable location (under otfnfv/src/otfnfv directory): "
read directory
sudo ln -s "$directory/src/otfnfv/otfnfv.py" "/bin/otfnfv"
echo "[OK] Created symbolic link to executable"
