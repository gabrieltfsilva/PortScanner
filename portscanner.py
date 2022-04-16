# PortScanner

"""
Written in python 3. Not tested on legacy versions.
Tested on Windows 11 and Debian 10.

Usage
python portscanner.py host -p 80 -v
host: address to scan.

-h, --help: show help
-p: ports, [common], all, 80, 20-25
-v: verbose

Host can be an ip address, a URL, a full range 0/24 or a txt file with a list.
Ports can be "common", "all", ports "20 21 1433" or ranges "20-25 8000-9000".
Verbose shows every step.
"""

import ipaddress
import sys
import argparse
import socket

from dataclasses import replace
from datetime import datetime
from enum import IntEnum

ERROR_HOST = 'Host not found.'
ERROR_FILE = 'File not found.'
ERROR_UNKNOWN = 'Unknown Error.'
MSG_OPEN = 'port open'
MSG_CLOSED = 'port closed'

class Errors(IntEnum):
    NoError = 0
    HostNotFound = 1
    FileNotFound = 2

lastError = Errors.NoError

def verifyIP(ip):
    try:
        verify = ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def verifyURL(url):
    try:
        return socket.gethostbyname(url)
    except:
        return False

def commonPorts():
    ports = [
        20, 21, 22, 23, 25, 53, 80, 109, 110, 115, 143, 156, 161, 194, 220, 443, 445, 465, 502, 563, 
        587, 989, 990, 993, 995, 1433, 1434, 1521, 1522, 1526, 2483, 2484, 3306, 5432, 8080, 27017
    ]
    return ports

def allPorts():
    ports = range(1, 65536)
    return ports

def getHosts(host):
    if verifyIP(host):
        return [host]
    elif host.endswith('.0/24'):
        values = range(1, 255)
        list = []
        for value in values:
            list.append(host.replace('0/24', str(value)))
        return list
    elif host.endswith('.txt'):
        try:
            values = open(host,'r') 
        except IOError:
            global lastError
            lastError = Errors.FileNotFound
            return []
        list = []
        for value in values:
            list.append(value.replace('\n', ''))
        return list
    else:
        return [host]

def getPorts(port):
    if (not port):
        return commonPorts()
    elif (port[0] == 'common' or not port):
        return commonPorts()
    elif (port[0] == 'all'):
        return allPorts()
    else:
        list = []
        for value in port:
            if (value.isdigit()):
                if (int(value) > 0 and int(value) < 65536):
                    list.append(int(value))
            else:
                arr = value.split('-')
                if ((len(arr) == 2) and arr[0].isdigit() and arr[1].isdigit()):
                    newArr = range(int(arr[0]), int(arr[1]) + 1)
                    for arrValue in newArr:
                        if (arrValue > 0 and arrValue < 65536):
                            list.append(arrValue)

        if (not list):
            return commonPorts()

        return list

def scanPort(ip, port):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(0.1)
        result = client.connect_ex((ip, port))
        client.close()
        if (result == 0):
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

def parse_input():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', nargs=1, help='host.com, 192.168.0.100, 192.168.0.0/24, list.txt')
    parser.add_argument('-p', nargs='*', default=['common'], help='ports, [common], all, 80, 20-25')
    parser.add_argument('-v', nargs='?', default=False, const=True, help='verbose')

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit()

    return parser.parse_args()

if __name__ == '__main__':
    print('\nScan Started.')
    arg = parse_input()
    host = arg.host[0]
    port = arg.p

    hosts = getHosts(host)
    ports = getPorts(port)

    if (not hosts):
        if (lastError == Errors.FileNotFound):
            print(ERROR_FILE)
            sys.exit()
        else:
            print(ERROR_UNKNOWN)
            sys.exit()

    openPorts = []

    for value1 in hosts:
        print('\n' + value1)
        hostIP = verifyURL(value1)
        if (hostIP):
            for value2 in ports:
                scanning = hostIP + ':' + str(value2)
                if (arg.v):
                    print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ': scanning ' + scanning)
                    if (scanPort(hostIP, value2)):
                        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ': port ' + str(value2) + ' open')
                        openPorts.append(value1 + ' - ' + scanning + ' open')
                    else:
                        print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ': port ' + str(value2) + ' closed')
                elif (scanPort(hostIP, value2)):
                    openPorts.append(value1 + ' - ' + scanning + ' open')
                    print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ': port ' + str(value2) + ' open')
        else:
            print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ': ' + value1 + ': ' + ERROR_HOST)

    print('\nScan Finished.\n')
    
    if (len(openPorts) > 0):
        for openPort in openPorts:
            print(openPort)
        print('')
    else:
        print('No ports open\n')
