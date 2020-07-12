#! /bin/bash

# variables declarations
country_code='FR'
local_ssid='***********'
local_psk='***********'
ap_ssid='SQRT_AP'
ap_psk='SQRT_AP_PASS'

#sudo read -p "Please enter an existing Network SSID:" local_ssid
#sudo read -s -p "Enter Password: " local_psk

# disable debian networking and dhcpcd
systemctl mask networking.service dhcpcd.service
sudo mv /etc/network/interfaces /etc/network/interfaces~
sed -i '1i resolvconf=NO' /etc/resolvconf.conf

# enable systemd-networkd
systemctl enable systemd-networkd.service systemd-resolved.service
ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf

# write wpa_supplicant files
{
	printf "country=%s\n" "$country_code";
	echo "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev";
	echo "update_config=1";
	echo "";
	echo "network={";
	printf '    ssid="%s"\n' "$local_ssid";
	printf '    psk="%s"\n' "$local_psk";
	echo "}"
} > /etc/wpa_supplicant/wpa_supplicant-wlan0.conf

{
	printf "country=%s\n" "$country_code";
	echo "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev";
	echo "update_config=1";
	echo "network={";
	printf '    ssid="%s"\n' "$ap_ssid";
	echo "    mode=2";
	echo "    key_mgmt=WPA-PSK";
	echo "    proto=RSN WPA";
	printf '    psk="%s"\n' "$ap_psk";
	echo "   frequency=2412";
	echo "}"
} > /etc/wpa_supplicant/wpa_supplicant-ap0.conf
# write network files
{
	echo "[Match]";
	echo "Name=wlan0";
	echo "[Network]";
	echo "DHCP=yes";
} > /etc/systemd/network/08-wlan0.network

{
	echo "[Match]";
	echo "Name=ap0";
	echo "[Network]";
	echo "Address=192.168.4.1/24";
	echo "DHCPServer=yes";
	echo "[DHCPServer]";
	echo "DNS=84.200.69.80 1.1.1.1";
} > /etc/systemd/network/12-ap0.network

# edit service
systemctl disable wpa_supplicant@ap0.service
{
	echo "[Unit]";
	echo "Description=WPA supplicant daemon (interface-specific version)";
	echo "Requires=sys-subsystem-net-devices-wlan0.device";
	echo "After=sys-subsystem-net-devices-wlan0.device";
	echo "Conflicts=wpa_supplicant@wlan0.service";
	echo "Before=network.target";
	echo "Wants=network.target";
	echo "";
	echo "# NetworkManager users will probably want the dbus version instead.";
	echo "";
	echo "[Service]";
	echo "Type=simple";
	echo "ExecStartPre=/sbin/iw dev wlan0 interface add ap0 type __ap";
	echo "ExecStart=/sbin/wpa_supplicant -c/etc/wpa_supplicant/wpa_supplicant-%I.conf -Dnl80211,wext -i%I";
	echo "ExecStopPost=/sbin/iw dev ap0 del";
	echo "";
	echo "[Install]";
	echo "Alias=multi-user.target.wants/wpa_supplicant@%i.service";
} > /tmp/sqrt_systemd_conf
sudo env SYSTEMD_EDITOR="cp /tmp/sqrt_systemd_conf" systemctl edit --full wpa_supplicant@ap0.service
# Select client mode on boot:
sudo systemctl enable wpa_supplicant@wlan0.service
sudo systemctl disable wpa_supplicant@ap0.service

echo "Wifi configured, you must reboot now !"