#!/usr/bin/env python3

import json
import os
import subprocess
import sys


DATA_FILE = "/home/user/.db.json"
LAN_IF = "em0"
WIFI_IF = "iwn0"


def usage():
    print("usage: doas " + sys.argv[0] + " connect (c)", file=sys.stderr)
    print("usage: doas " + sys.argv[0] + " neuter (n)", file=sys.stderr)
    print("usage: doas " + sys.argv[0] + " register (r)", file=sys.stderr)
    print("usage: doas " + sys.argv[0] + " trunk (t)", file=sys.stderr)
    print("usage: " + sys.argv[0] + " list (l)", file=sys.stderr)


def askinfo():
    network = input("network name ")
    ssid = input("SSID? ")
    password_type = input("password type? (no, wpa, wep) ")

    if password_type == "no":
        password = "withoutpassword"
    elif password_type == "wpa" or "wep":
        password = input("password? ")
    else:
        print("Wrong type, try again")
        sys.exit("1")
    return network, ssid, password_type, password


def register():
    network, ssid, password_type, password = askinfo()
    print(network, ssid, password_type, password)

    networkjson = {'SSID':
                   ssid, 'password_type': password_type, 'password': password}
    netjson = {network: networkjson}

    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    data.update(netjson)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)
    return network


def listnetwork():
    print("lan")
    print("lan6")
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    for k, v in data.items():
        print(k)


def printer(network=None):
    if network:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

        try:
            # to detect the except
            ssid = data[network]["SSID"]
            print("\033[0;35mnetwork : \033[1;35m" + network)
            print("\033[0;34m  SSID: \033[1;34m" + ssid)
            print("\033[0;33m  password: \033[1;33m" +
                  data[network]["password"])
        except KeyError:
            print("No such network", file=sys.stderr)
            sys.exit(1)


def genhostnameif(network):
    if network == "lan" or network == "lan6":
        hostnameif = "/etc/hostname." + LAN_IF
        with open(hostnameif, "w") as f:
            f.write("dhcp\n")
            if network == "lan6":
                f.write("inet6 autoconf")
    else:
        hostnameif = "/etc/hostname." + WIFI_IF
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

        with open(hostnameif, "w") as f:
            try:
                f.write("nwid " + data[network]["SSID"] + "\n")
                if data[network]["password_type"] == "wpa":
                    f.write("wpakey " + data[network]["password"] + "\n")
                elif data[network]["password_type"] == "wep":
                    f.write("nwkey " + data[network]["password"] + "\n")
                f.write("dhcp\n")
            except KeyError:
                print("No such network", file=sys.stderr)
                sys.exit(1)


def gentrunkhostnameif(network):
    hostnameif = "/etc/hostname." + LAN_IF
    with open(hostnameif, "w") as f:
        f.write("up\n")

    hostnameif = "/etc/hostname." + WIFI_IF
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    with open(hostnameif, "w") as f:
        try:
            f.write("nwid " + data[network]["SSID"] + "\n")
            if data[network]["password_type"] == "wpa":
                f.write("wpakey " + data[network]["password"] + "\n")
            elif data[network]["password_type"] == "wep":
                f.write("nwkey " + data[network]["password"] + "\n")
            f.write("up\n")
        except KeyError:
            print("No such network", file=sys.stderr)
            sys.exit(1)
    with open("/etc/hostname.trunk0", "w") as f:
        f.write("trunkproto failover trunkport " + LAN_IF + "\n")
        f.write("trunkport " + WIFI_IF + "\n")
        f.write("dhcp\n")


def connect(network=None, trunk="no"):
    netclean()
    if not network:
        network = input("which network? ")
    if trunk == "yes":
        gentrunkhostnameif(network)
    else:
        genhostnameif(network)

    subprocess.call(['chmod 0640 /etc/hostname.*'], shell=True)
    subprocess.call(['sh /etc/netstart'], shell=True)


def netclean():
    subprocess.call(['/sbin/ifconfig ' + WIFI_IF +
                     ' -nwid -wpakey -nwkey -bssid'], shell=True)
    subprocess.call(['/sbin/ifconfig ' + WIFI_IF + ' down'], shell=True)
    subprocess.call(['/sbin/ifconfig ' + LAN_IF + ' down'], shell=True)
    subprocess.call(['/sbin/ifconfig ' + LAN_IF + ' -inet'], shell=True)
    subprocess.call(['/sbin/ifconfig trunk0 destroy 2>/dev/null'], shell=True)

    if os.path.isfile("/etc/hostname.trunk0"):
        os.remove("/etc/hostname." + WIFI_IF)
        os.remove("/etc/hostname." + LAN_IF)
        os.remove("/etc/hostname.trunk0")
    elif os.path.isfile("/etc/hostname." + LAN_IF):
        os.remove("/etc/hostname." + LAN_IF)
    elif os.path.isfile("/etc/hostname." + WIFI_IF):
        os.remove("/etc/hostname." + WIFI_IF)


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "register" or sys.argv[1] == "r":
            newnet = register()
            connect(network=newnet)
        elif sys.argv[1] == "list" or sys.argv[1] == "l":
            if len(sys.argv) > 2:
                printer(network=sys.argv[2])
            else:
                listnetwork()
        elif sys.argv[1] == "connect" or sys.argv[1] == "c":
            if len(sys.argv) > 2:
                connect(network=sys.argv[2])
            else:
                connect()
        elif sys.argv[1] == "neuter" or sys.argv[1] == "n":
            netclean()
        elif sys.argv[1] == "trunk" or sys.argv[1] == "t":
            if len(sys.argv) > 2:
                connect(network=sys.argv[2], trunk="yes")
            else:
                connect(trunk="yes")
        else:
            usage()
    else:
        usage()


if __name__ == "__main__":
    main()
