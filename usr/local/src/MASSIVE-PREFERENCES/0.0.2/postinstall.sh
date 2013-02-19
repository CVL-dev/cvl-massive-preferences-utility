#!/bin/bash

rm -f /usr/lib/bonobo/servers/massivePreferencesApplet.server
ln -s `find /usr/local/massive-preferences/ -iname '*.server'` /usr/lib/bonobo/servers/massivePreferencesApplet.server


easy_install pip
pip install ssh


mkdir /home/projects
chmod a+rwx /home/projects

echo "user_allow_other" > /etc/fuse.conf


latest=`ls /usr/local/massive-preferences/ | sort | tail -1`

cp -r /usr/local/massive-preferences/${latest}/massive-preferences/etc/skel/.config /etc/skel/



