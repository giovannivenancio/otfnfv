# On-The-Fly NFV

On-The-Fly NFV is a tool that instantiate, remove and manage Virtualized Network Functions (VNFs) in real time. This tool provides a simple and intuitive way to create specific filters that are applied to packet flows and that determines to which VNFs packets should be forwarded.

## Prerequisites

On-The-Fly NFV tool is built upon Ryu Controller, MongoDB and Mininet. Make sure to have those installed on the system.

* [Ryu](https://osrg.github.io/ryu/) - OpenFlow Controller
* [Mininet](http://mininet.org/) - Virtual Network
* [MongoDB](https://www.mongodb.com/) - Database

## Installing

After installing the prerequisites, follow these steps to install the On-The-Fly NFV tool:

```
# Install Mininet
git clone git://github.com/mininet/mininet
sudo mininet/util/install.sh -a

# Install Ryu Controller
git clone git://github.com/osrg/ryu.git
sudo python ryu/setup.py install

# Clone On-The-Fly NFV source code.
git clone https://github.com/giovannivenancio/otfnfv.git

# Change to installation directory.
cd ./otfnfv/install/

# Execute 'setup.py' and 'install_packages.sh' script.
# These scripts will install necessary packages and libraries.
sudo ./setup.py install
sudo ./install_packages.sh

# Edit 'otfnfv.conf.example' file and replace "remote_host" and
# both "path" information.
vim otfnfv.conf.example

# Execute 'config.sh' script. This script will get information
# about some paths and will create on system some required files.
sudo ./config.sh

# Execute 'create_db.py' script. This script will create
# and populate the database.
./create_db.py

# Finally, edit '/etc/mongod.conf' file and replace "bindIp: 127.0.0.1"
# with "bindIp: 0.0.0.0". This is required because there is a
# communication between host (where MongoDB Server is running)
# and Mininet host (where MongoDB Client is running).
sudo vim /etc/mongod.conf
sudo service mongod restart
```

After that, the tool should be running properly.
To run:

```
sudo otfnfv
```

## Built With

* [Python](https://www.python.org/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
