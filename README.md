# Squirrel_detector
Squirrel_detector

add a cron:
```
@reboot sudo rfkill unblock wifi && cd /home/pi/Squirrel_detector && sudo python3 Squirrel_detector.py &
```
