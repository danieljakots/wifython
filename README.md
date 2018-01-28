# wifython

Wifi managed with python (for OpenBSD).

It configures [hostname.if(5)](https://man.openbsd.org/hostname.if)
files and runs [ifconfig(8)](https://man.openbsd.org/ifconfig) if
needed so it obviously needs to run as root.

It stores the known wifi in a json file for the mere reason I wanted
to learn how to deal with json with python.

It was written in December 2016 and it's not actively maintained but
it is actively used by yours truly (and it works fine for my needs,
which may not me yours).

To use it, just edit the script with:
* the path of the json database
* your lan interface
* your wifi interface


~~~
# python3 wifython.py
usage: doas wifython.py connect (c)
usage: doas wifython.py neuter (n)
usage: doas wifython.py register (r)
usage: doas wifython.py trunk (t)
usage: wifython.py list (l)
~~~

but reading the script is advised :)
