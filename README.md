# Squirrel_detector
Squirrel_detector

add a cron:
```
@reboot sudo rfkill unblock wifi && cd /home/pi/Squirrel_detector && sudo python3 Squirrel_detector.py &
```

run diff (first import images from RPi and clean images to make first one reference):
```
python3 out/photo_diff.py
```
