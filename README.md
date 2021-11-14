# HilldustWrapper
And a wrapper to the original Hilldust (https://github.com/LionNatsu/hilldust) to provide the following functionalities:

 - Read configurations from an user-specified file
 - Process the route table returned from VPN server, and allow custom routes
 - Add a systemd service to startup the VPN at system startup
 - Use nmcli instead of iproute2 for network configuration

# Requirements

 - Python 3
 - scapy (Python module)
 - cryptography (Python module)
 - nmcli

# Usage

Parameters are read from a json configuration file. Here is an example,

```json
{
    "server": "10.6.0.254",
    "port": 8888,
    "user": "username@domain",
    "pass": "password",
    "routes": [
        "10.6.0.0/24",
        "10.7.0.0/24"
    ]
}
```

Usually the routes field is not needed, use it only when you have special routes not in the returned route table.

The VPN can be started from the command line via

```bash
sudo ./hilldustWrapper.py -c [CONFIG_FILE]
```

It can also be started as a systemd service. An example service file is provided in systemd/hilldustWrapper.service. You may also use the install.py to configure the systemd service and start it automatically at system startup

```bash
sudo ./install.py -c [CONFIG_FILE]
```

# Notes

For Centos 7, the distro version of pip/scapy/cryptography are outdated. You
may need to upgrade them via pip.

```bash
sudo python3 -m pip install --upgrade pip
sudo python3 -m pip install --upgrade scapy
sudo python3 -m pip install --upgrade cryptography
```

For Centos 8, the distro version is sufficient, you may install them via

```bash
sudo dnf install python3-scapy
sudo dnf install python3-cryptography
```

The 3DES crypto is disabled by default in Centos 8, you may enable it via

```bash
sudo update-crypto-policies --set LEGACY
```
