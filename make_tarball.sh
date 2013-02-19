#!/bin/bash

set -x

VERSION=$1

rm -fr massive-preferences
mkdir massive-preferences
mkdir massive-preferences/bin
mkdir massive-preferences/lib
mkdir massive-preferences/etc

cp massivePreferencesApplet.py massive-preferences/bin/
cp MASSIVElogoTransparent32x32.xpm massivePreferencesApplet.server Massive*.desktopmassive-preferences/lib
cp -vr etc massive-preferences

touch massive-preferences/readme.txt
cd massive-preferences/lib
sed -i "s/CVLMASSIVEPREFERENCESVERSION/${VERSION}/g" massivePreferencesApplet.server 
sed -i "s/CVLMASSIVEPREFERENCESVERSION/${VERSION}/g" "Massive Preferences.desktop"
cd -

tar zcvf massive-preferences-${VERSION}.tar.gz massive-preferences
rm -fr massive-preferences

