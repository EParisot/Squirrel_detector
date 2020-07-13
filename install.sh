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
if ! mountpoint -q /boot; then
return 1
fi
[ -e /boot/config.txt ] || touch /boot/config.txt
set_config_var start_x 1 /boot/config.txt
CUR_GPU_MEM=$(get_config_var gpu_mem /boot/config.txt)
if [ -z "$CUR_GPU_MEM" ] || [ "$CUR_GPU_MEM" -lt 128 ]; then
    set_config_var gpu_mem 128 /boot/config.txt
fi
sed /boot/config.txt -i -e "s/^startx/#startx/"
sed /boot/config.txt -i -e "s/^fixup_file/#fixup_file/"
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