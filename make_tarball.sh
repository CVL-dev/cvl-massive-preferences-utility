#!/bin/bash

set -x

VERSION=$1

rm -fr cvl-massive-preferences
mkdir cvl-massive-preferences
cp MASSIVElogoTransparent32x32.xpm massivePreferencesApplet.py massivePreferencesApplet.server cvl-massive-preferences
cd cvl-massive-preferences
sed -i "s/CVLMASSIVEPREFERENCESVERSION/${VERSION}/g" massivePreferencesApplet.server 
cd ..

tar zcvf cvl-massive-preferences-${VERSION}.tar.gz cvl-massive-preferences
rm -fr cvl-massive-preferences

