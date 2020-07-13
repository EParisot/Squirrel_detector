#! /bin/bash
echo -e "\e[33mInstalling Dependencies... \e[0m"
# system dep
apt-get update
apt-get install python3-dev python3-setuptools python3-pip python3-picamera -y
# check python/pip versions
python3 -c 'import sys; print("Please update your Python version to 3.5 or later...", exit(1)) if sys.version_info.major < 3 or sys.version_info.minor < 5 else print("Python version checked")'
# package dep
pip3 install -r requirements.txt
# activate camera
echo -e "\e[33mActivating Camera... \e[0m"
raspi-config nonint do_camera 0
# activate i2c
echo -e "\e[33mActivating i2c... \e[0m"
raspi-config nonint do_i2c 0
# set crontab
echo -e "\e[33mAdd crontab... \e[0m"
(crontab -l -u pi ; echo "@reboot cd Squirrel_detector && sudo python3 Squirrel_detector.py &") | sort - | uniq - | crontab - -u pi
# set Wifi
echo -e "\e[33mSet Wifi... \e[0m"
./set_wifi.sh
# ask for reboot
read -p "Reboot Now (needed to restart wifi settings) ? (y/n)" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    reboot
fi