from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("config.html")

@app.route("/configure", methods=["POST"])
def configure():
    ssid = request.form["ssid"]
    password = request.form["password"]

    # Save the entered Wi-Fi credentials for further processing
    save_wifi_credentials(ssid, password)

    return "Configuration successful!"

def save_wifi_credentials(ssid, password):
    # Perform necessary actions to save the Wi-Fi credentials
    # to be used for connecting to the user's home network
    print(f"SSID: {ssid}, Password: {password}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
