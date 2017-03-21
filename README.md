# On-The-Fly NFV

One Paragraph of project description goes here

On-The-Fly NFV is a tool that instantiate, remove and manage Virtualized Network Functions (VNFs) in real time. This tool provides a simple and intuitive way to create specific filters that are applied to packet flows and that determines to which VNFs packets should be forwarded.

## Prerequisites

On-The-Fly NFV tool is built upon Ryu Controller, MongoDB and Mininet. Make sure to have those installed on the system.

* [Ryu](https://osrg.github.io/ryu/) - OpenFlow Controller
* [Mininet](http://mininet.org/) - Virtual Network
* [MongoDB](https://www.mongodb.com/) - Database

## Installing

After installing the prerequisites, follow these steps to install the On-The-Fly NFV tool:

```
git clone https://github.com/giovannivenancio/otfnfv.git
cd ./otfnfv/install/
configura arquivo conf.example
executar config.sh (falar sobre ele - o que faz)
executar createdb ("")
configurar mongodb
executar setup (falar ...)
```

After that, the tool should be running properly.

To run:

```
sudo otfnfv
```

## Built With

* [Python](https://www.python.org/) - The web framework used

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
