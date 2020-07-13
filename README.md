# SQuareRooT Project
#### Capture wildlife from your garden !

![](imgs/1591654076.6840587.jpg)
![](imgs/download_20200602_151311.jpg)

## Material:
* RaspberryPi + SD card : [Shop](https://www.amazon.fr/Raspberry-Pi-3-Mod%C3%A8le-B-Carte-m%C3%A8re/dp/B07BDR5PDW/ref=sr_1_10?__mk_fr_FR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&dchild=1&keywords=raspberry&qid=1591701953&s=computers&sr=1-10)
(any RPi model will fit, maybe avoid using a RPi4 (overkill + heat))
* Camera : [Shop](https://www.amazon.fr/Waveshare-Raspberry-Camera-Fisheye-Raspberry-pi/dp/B00W9BIVL8/ref=pd_day0_147_5/260-5767670-7540537?_encoding=UTF8&pd_rd_i=B00RMV53Z2&pd_rd_r=eada2bcf-6cba-4e5f-a39d-fc42470e45ef&pd_rd_w=x8LDt&pd_rd_wg=npx3k&pf_rd_p=d0e20867-8bc1-4681-ae06-595fd1a37cc6&pf_rd_r=6PFJGPFVSA3QQK30FEJT&refRID=6PFJGPFVSA3QQK30FEJT&th=1)
* ToF distance sensor : [Shop](https://www.amazon.fr/gp/product/B07RWT9D5Z/ref=ppx_yo_dt_b_asin_title_o07_s00?ie=UTF8&psc=1)
* Battery pack : [Shop](https://www.amazon.fr/gp/product/B07HK5VGB6/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1)
* Button [Shop](https://www.amazon.fr/AZDelivery-Interrupteur-capteur-dinterrupteur-Arduino/dp/B089QK4XLR/ref=bbp_recs_dp_dt_1/257-4051293-5651547?_encoding=UTF8&pd_rd_i=B07DPSMRJ6&pd_rd_r=c0ee2955-ff45-4b5e-82aa-37a583ebaa29&pd_rd_w=6mDj2&pd_rd_wg=bJZ3K&pf_rd_p=c4d255f6-5d10-4c39-9dc8-d12aa0a8b41d&pf_rd_r=850SJQ1W4SW9WB5JTN8Q&refRID=850SJQ1W4SW9WB5JTN8Q&th=1 )
* Light sensor [Shop](https://www.amazon.fr/Photor%C3%A9sistances-GL5539-30K-90K-d%C3%A9pendant-lumi%C3%A8re/dp/B01EZZMLOI/ref=bbp_recs_dp_dt_14?_encoding=UTF8&pd_rd_i=B01EZZMLOI&pd_rd_r=6f7f80fd-d129-4488-8cc5-06dad9d953d3&pd_rd_w=jHot5&pd_rd_wg=m3krl&pf_rd_p=c4d255f6-5d10-4c39-9dc8-d12aa0a8b41d&pf_rd_r=XME3CPC169JASQZ5ETMR&psc=1&refRID=XME3CPC169JASQZ5ETMR)
* Jumper cables, 1 Capacitor (1microf), 1 led, 1 resistor (330 ohms)


# Instructions:

Based on Raspberry Pi Zero W
Raspberry Pi OS (32-bit) Lite
Minimal image based on Debian Buster
Version:May 2020


### Wire Camera, distance sensor, button, led, everything !

scheme to come...

### Clone the repo on the RPi and install
```
sudo apt-get install git
git clone https://github.com/EParisot/Squirrel_detector.git
cd Squirrel_detector
sudo ./install.sh
```
(You will be asked for some interractions while setting wifi... stay focused !)

### Reboot, find a great spot and ... enjoy the show ! 

Everything is made to save up battery life: WIFI stay shutted down until you press the button (no picture can be taken during this time), HDMI is stopped on boot.

A camera test shot is made on start, everything is logged in activity.log file.

If the brightness is not sufficient, no sensor will be triggered for 10 min to avoid black images (and prevent useless power consumption)

A compagnon App is also in progress and will allow user to download images from the device. Start App, press the button and download your pictures on the phone.

## Usefull commands:
Start the STA (wifi client) mode :
```
sudo systemctl start wpa_supplicant@wlan0.service
```
Start the AP (wifi server) mode :
```
sudo systemctl start wpa_supplicant@ap0.service
```
Restart HDMI port :
```
sudo /usr/bin/tvservice -p
(-o to stop)
```

## Licensing
This project is under MIT license which means you can share, use, modify it if you cite the author (me)... Thanks !

