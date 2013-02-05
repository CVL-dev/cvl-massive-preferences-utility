cvl-massive-preferences-utility
===============================

Utility for mounting Massive project directories on a CVL instance.

Drop gnomeAppletExample.server in

    /usr/lib/bonobo/servers

and beware that gnomeAppletExample.py needs to be in /home/carlo.

Make sure that /etc/fuse.conf has this line:

    user_allow_other

DEPENDENCIES
============

* python-gnome library
* python-devel
* ssh (use pip)

