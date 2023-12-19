import subprocess
import time
from flask import Flask, render_template, request
from threading import Thread

app = Flask(__name__)

def check_wifi_connection():
    try:
        # Use subprocess to check if wlan0 has an IP address
        result = subprocess.check_output(['iwconfig', 'wlan0'])
        return b'Not-Associated' not in result
    except subprocess.CalledProcessError:
        return False

def enable_own_ap():
    # Add your code to enable your own access point here
    # This may include configuring hostapd, dnsmasq, etc.
    print("Enabling own access point")

    # Stop the wpa_supplicant service
    subprocess.run(['sudo', 'systemctl', 'stop', 'wpa_supplicant'])

    # Configure the wlan0 interface with a static IP address
    subprocess.run(['sudo', 'ifconfig', 'wlan0', '192.168.4.1', 'netmask', '255.255.255.0'])

    # Start the hostapd service with the previously configured file
    subprocess.run(['sudo', 'systemctl', 'start', 'hostapd'])

    # Start the dnsmasq service
    subprocess.run(['sudo', 'systemctl', 'start', 'dnsmasq'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/configure', methods=['POST'])
def configure():
    ssid = request.form['ssid']
    password = request.form['password']

    # Build the new network configuration
    new_network_config = f'''
network={{
    ssid="{ssid}"
    psk="{password}"
}}
'''

    wpa_supplicant_path = '/etc/wpa_supplicant/wpa_supplicant.conf'

    # Append the new network configuration to the existing wpa_supplicant.conf file
    try:
        with open(wpa_supplicant_path, 'a') as wpa_supplicant_file:
            wpa_supplicant_file.write(new_network_config)
    except Exception as e:
        return f'Error adding to wpa_supplicant.conf: {e}'

    # Use nmcli to add a new Wi-Fi network
    try:
        subprocess.run(['sudo', 'nmcli', 'device', 'wifi', 'connect', ssid, 'password', password], check=True)
        
        # If both operations are successful, trigger a reboot
        try:
            subprocess.run(['sudo', 'reboot'], check=True)
        except subprocess.CalledProcessError as e:
            return f'Error rebooting: {e}'

        return 'Configuration applied successfully! Rebooting...'
    except subprocess.CalledProcessError as e:
        return f'Error adding to Network Manager: {e}'

@app.route('/enable_ap')
def enable_ap():
    enable_own_ap()
    return 'Access Point enabled!'

def start_flask():
    app.run(host='0.0.0.0', port=80)

def main():
    # Wait for some time to allow the system to connect to Wi-Fi
    time.sleep(30)

    if not check_wifi_connection():
        enable_own_ap()
        # Start Flask in a separate thread
        flask_thread = Thread(target=start_flask)
        flask_thread.start()
    else:
        print("WiFi connection is established.")

        # Enter code here to start the pilamp service

if __name__ == '__main__':
    main()
