# HilldustWrapper
And a wrapper to the original Hilldust (https://github.com/LionNatsu/hilldust) to provide the following functionalities:

 - Read configurations from an user-specified file
 - Allow custom routes (the original may not work for some VPN configuration)
 - Add a systemd service to startup the VPN at system startup
 - Use nmcli instead of iproute2 for network configuration (to avoid conflict with NetworkManager)

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

The VPN can be started from the command line via

```bash
sudo ./hilldustWrapper.py -c [CONFIG_FILE]
```

It can also be started as a systemd service. An example service file is provided in systemd/hilldustWrapper.service. You may also use the install.py to configure the systemd service and start it automatically at system startup

```bash
sudo ./install.py -c [CONFIG_FILE]
```
