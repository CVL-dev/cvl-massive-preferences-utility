#!/bin/bash

rm -f /usr/lib/bonobo/servers/massivePreferencesApplet.server
ln -s `find /usr/local/massive-preferences/ -iname '*.server'` /usr/lib/bonobo/servers/massivePreferencesApplet.server

