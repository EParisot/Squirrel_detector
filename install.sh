#! /bin/bash
# system dep
apt-get update
apt-get install python3-dev python3-setuptools python3-pip python3-picamera -y
# check python/pip versions
python3 -c 'import sys; print("Please update your Python version to 3.5 or later...", exit(1)) if sys.version_info.major < 3 or sys.version_info.minor < 5 else print("Python version checked")'
# package dep
pip3 install -r requirements.txt
# all Done !
echo "Dependencies Installation Done !"
# activate camera
raspi-config nonint do_camera 0
# set Wifi
./set_wifi.sh
# set crontab
(crontab -l ; echo "@reboot cd Squirrel_detector && sudo python3 Squirrel_detector.py &") | sort - | uniq - | crontab -
# ask for reboot
read -p "Reboot Now (needed to restart wifi settings) ? (y/n)" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    reboot
fi