cvl-massive-preferences-utility
===============================

Utility for mounting Massive project directories on a CVL instance.

Drop massivePreferencesApplet.server in

    /usr/lib/bonobo/servers

and beware that massivePreferencesApplet.py needs to be in a particular
location (refer to massivePreferencesApplet.server).

The string 'CVLMASSIVEPREFERENCESVERSION' in
massivePreferencesApplet.server needs to be changed to the version
number of the installed package.

Make sure that /etc/fuse.conf has this line:

    user_allow_other

Make sure that

    /home/projects

exists and is writable by normal users.

DEPENDENCIES
============

* yum -y install gnome-python2-applet python-devel
* easy_install pip; pip install ssh

