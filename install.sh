#! /bin/bash
# system dep
apt-get install python3-dev python3-setuptools python3-pip bluetooth libbluetooth-dev obexftp -y
# check python/pip versions
python3 -c 'import sys; print("Please update your Python version to 3.5 or later...", exit(1)) if sys.version_info.major < 3 or sys.version_info.minor < 5 else print("Python version checked")'
# package dep
pip3 install -r requirements.txt
# bluetooth files setting
cp config_files/main.conf /etc/bluetooth/main.conf
cp config_files/dbus-org.bluez.service /etc/systemd/system/dbus-org.bluez.service
cp config_files/machine-info /etc/machine-info