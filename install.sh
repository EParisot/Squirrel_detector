#! /bin/bash
# system dep
apt-get install python3-dev python3-setuptools python3-pip bluetooth libbluetooth-dev obexftp -y
# check python/pip versions
python3 -c 'import sys; print("Please update your Python version to 3.5 or later...", exit(1)) if sys.version_info.major < 3 or sys.version_info.minor < 5 else print("Python version checked")'
# package dep
pip3 install -r requirements.txt
# all Done !
echo "Installation Done !"
#read -p "Reboot Now? (y/n)" -n 1 -r
#echo    # (optional) move to a new line
#if [[ $REPLY =~ ^[Yy]$ ]]
#then
#    reboot
#fi