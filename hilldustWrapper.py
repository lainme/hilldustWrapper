#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import argparse
import json
from pathlib import Path
import hilldust.impl_scapy
import fcntl
import struct
import subprocess
import re
import os
import time
import signal
import ipaddress
from threading import Thread
import sys

class ClientSendThread(Thread):
    def __init__(self, con, tun):
        Thread.__init__(self)
        self.daemon = True
        self.con = con
        self.tun = tun
    def __read(self):
        return os.read(self.tun.fileno(), 8192)
    def run(self):
        while True:
            raw = self.__read()
            self.con.send(raw)

class ClientRecvThread(Thread):
    def __init__(self, con, tun):
        Thread.__init__(self)
        self.daemon = True
        self.con = con
        self.tun = tun
    def __write(self, datagram:bytes):
        os.write(self.tun.fileno(), datagram)
    def run(self):
        while True:
            raw = self.con.recv()
            self.__write(raw)

class HilldustDaemon():
    def __init__(self, config):
        self.config = config
        self.conn = ''
        self.uuid = ''
        self.name = ''
        self.kill = False
        signal.signal(signal.SIGINT, self.__close_handle)
        signal.signal(signal.SIGTERM, self.__close_handle)
    def create_connection(self):
        # Connect to VPN (reproduced from hilldust.py)
        self.conn = hilldust.impl_scapy.Client()
        self.conn.connect(self.config['server'], int(self.config['port']))
        print('Connected to server.')
        self.conn.auth(self.config['user'], self.config['pass'], '', '')
        print('Authentication completed.')
        self.conn.client_info()
        self.conn.wait_network()
        print('Got network configuration.')
        self.conn.new_key()
        print('Key exchanging completed.')

        # Configure network (modified from platform_linux.py)
        TUNSETIFF = 0x400454ca
        IFF_TUN = 0x0001
        IFF_NO_PI = 0x1000

        tun = open('/dev/net/tun', 'r+b', buffering=0)
        self.name = struct.pack('16sH', b'', IFF_TUN | IFF_NO_PI)
        self.name = fcntl.ioctl(tun, TUNSETIFF, self.name)
        self.name = self.name[:self.name.index(b'\0')].decode('ascii')

        command_output = subprocess.check_output('nmcli con add type tun ifname '+self.name+' con-name '+self.name+' mode tun', shell=True).decode('ascii')
        print(command_output)
        self.uuid = re.match('[^(]*\(([^)]*)\)', command_output).group(1)
        subprocess.check_call('nmcli con mod '+self.uuid+' ipv4.method manual ipv4.addr '+str(self.conn.ip_ipv4.ip), shell=True)
        for dns in self.conn.dns_ipv4:
            subprocess.check_call('nmcli con mod '+self.uuid+' +ipv4.dns '+str(dns), shell=True)
        subprocess.check_call('nmcli con mod '+self.uuid+' +ipv4.dns-priority 100', shell=True)
        for i in range(0, len(self.conn.route_ipv4), 12):
            ipv4Addr = str(ipaddress.IPv4Address(self.conn.route_ipv4[i:i+4]))
            ipv4Mask = str(ipaddress.IPv4Address(self.conn.route_ipv4[i+4:i+8]))
            ipv4Gate = str(self.conn.gateway_ipv4)
            ipv4Route = str(ipaddress.IPv4Network(ipv4Addr+'/'+ipv4Mask))+' '+ipv4Gate
            subprocess.check_call('nmcli con mod '+self.uuid+' +ipv4.routes "'+ipv4Route+'"', shell=True)
        subprocess.check_call('nmcli con mod '+self.uuid+' +ipv4.routes "'+str(self.conn.ip_ipv4.network)+' '+str(self.conn.gateway_ipv4)+'"', shell=True)
        try:
            for route in self.config['routes']:
                subprocess.check_call('nmcli con mod '+self.uuid+' +ipv4.routes "'+str(route)+' '+str(self.conn.gateway_ipv4)+'"', shell=True)
        except:
            pass
        subprocess.check_call('nmcli con up '+self.uuid, shell=True)
        print('Network configured.')

        # Threading (modified from hilldust.py and platform_linux.py)
        clientSendThread = ClientSendThread(self.conn, tun)
        clientRecvThread = ClientRecvThread(self.conn, tun)
        clientSendThread.start()
        clientRecvThread.start()

        # Keep busy
        while True:
            time.sleep(120)
            subprocess.call('nslookup '+str(self.conn.gateway_ipv4)+' '+str(self.conn.dns_ipv4[0]), shell=True, stdout=subprocess.DEVNULL)
    def __close_handle(self, signum, frame):
        self.__del__()
    def __del__(self):
        if not self.kill:
            print('Logout.')
            self.conn.logout()
            subprocess.check_call('nmcli con down '+self.uuid, shell=True)
            subprocess.check_call('nmcli con del '+self.uuid, shell=True)
            print('Network restored.')
            self.kill = True
        sys.exit()

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Wrapper of hilldust.")
    parser.add_argument("-c", dest="config", required=True, help="Path of the configuration file.")
    args = parser.parse_args()

    # Load configuration
    config = json.loads(Path(args.config).read_text())

    # Create connection
    hilldustDaemon = HilldustDaemon(config)
    hilldustDaemon.create_connection()

if __name__ == '__main__':
    main()
