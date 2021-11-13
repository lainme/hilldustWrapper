# HilldustWrapper
And a wrapper to the original Hilldust (https://github.com/LionNatsu/hilldust) to provide the following functionalities:

 - Read configurations from an user-specified file
 - Allow custom routes (the original may not work for some VPN configuration)
 - Add a systemd service to startup the VPN at system startup
 - Use nmcli instead of iproute2 for network configuration (to avoid conflict with NetworkManager)
