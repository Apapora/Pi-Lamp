import subprocess
import time
from flask import Flask, render_template

app = Flask(__name__)

def setup_access_point(ssid, password):
    # Stop the network manager service
    subprocess.run(["sudo", "systemctl", "stop", "NetworkManager"])

    # Configure the access point
    with open("/etc/hostapd/hostapd.conf", "w") as f:
        f.write(f"interface=wlan0\n")
        f.write(f"ssid={ssid}\n")
        f.write(f"hw_mode=g\n")
        f.write(f"channel=7\n")
        f.write(f"wpa=2\n")
        f.write(f"wpa_passphrase={password}\n")
        f.write(f"wpa_key_mgmt=WPA-PSK\n")
        f.write(f"wpa_pairwise=TKIP\n")
        f.write(f"rsn_pairwise=CCMP\n")

    # Start the access point
    subprocess.run(["sudo", "hostapd", "/etc/hostapd/hostapd.conf"])

def run_command(command):
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode().strip()


def stop_service(service):
    run_command(f"sudo systemctl stop {service}")


def start_service(service):
    run_command(f"sudo systemctl start {service}")


def is_service_active(service):
    status = run_command(f"systemctl is-active {service}")
    return status == "active"


def enable_hostapd_mode():
    stop_service("wpa_supplicant")
    time.sleep(30)
    start_service("hostapd")


def enable_wifi_mode():
    stop_service("hostapd")
    time.sleep(30)
    start_service("wpa_supplicant")


@app.route('/')
def index():
    return render_template('config.html')


if __name__ == "__main__":

    # Allow users to connect to the Raspberry Pi access point
    enable_hostapd_mode()
    app.run(host='0.0.0.0', port=80)  # Run Flask app

    # After 5 minutes, switch back to Wi-Fi mode
    time.sleep(300)
    enable_wifi_mode()
    time.sleep(30)
    start_service("wpa_supplicant")