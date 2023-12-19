
import command_line_utils as clu
from awsiot import mqtt5_client_builder
from awscrt import mqtt5, http
import RPi.GPIO as GPIO
from rpi_ws281x import PixelStrip, Color
import animations
from concurrent.futures import Future
import time,os,threading,subprocess,json, sys


#Example usage:
#sudo -E python3 ~/Git/aws_lamp/app/lamp/pi-lamp.py --endpoint $LAMP_ENDPOINT --ca_file ~/certs/AmazonRootCA1.pem --cert ~/certs/device.pem --key ~/certs/private.pem.key --client_id $LAMP_NAME --topic $LAMP_TOPIC --count 0

device = os.environ["LAMP_NAME"]
my_color_word = os.environ.get("LAMP_COLOR").lower()
my_color_rgb = animations.color_to_rgb(my_color_word)
my_color_hex = animations.color_to_hex(my_color_word)
lamp_topic = os.environ.get("LAMP_TOPIC")
print(f"Lamp set with RGB: {my_color_rgb} of type {type(my_color_rgb)}", flush=True)
print(f"Lamp set with hex: {my_color_hex}", flush=True)

TIMEOUT = 100
idle = True

# LED strip configuration:
LED_COUNT = 55        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 150  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# cmdData is the arguments/input from the command line placed into a single struct for
# use in this sample. This handles all command line parsing, validating, etc.
# See the Utils/CommandLineUtils for more information.
cmdData = clu.CommandLineUtils.parse_sample_input_mqtt5_pubsub()

#received_count = 0
future_stopped = Future()
future_connection_success = Future()

def run_git_pull():
    # Define the command and arguments
    cmd = ["git", "pull"]
    env = os.environ.copy()
    env['HOME'] = '/home/pir'
    env['USER'] = 'pir'

    # Run the command as the "pir" user in a new session
    try:
        subprocess.Popen(cmd, cwd="/home/pir/Git/aws_lamp", user="pir", start_new_session=True)
        print("Git pull started successfully.")
        send_message({'device': device, 'action': 'git', 'status': 'success'})
    except Exception as e:
        print(f"Git pull failed with error: {e}")
        send_message({'device': device, 'action': 'git', 'status': 'error'})


def run_command(command, sudo=False):
    try:
        if sudo:
            process = subprocess.Popen(command, user="root", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True)
        else:
            process = subprocess.Popen(command, user="pir", shell=True, text=True,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if stdout:
            print("Command executed successfully.")
            print("Output:")
            send_message({"device": device, "status": "command successful", "return": stdout})

        if stderr:
            print("Error messages:")
            send_message({"device": device, "status": "command error", "return": stderr})

        if process.returncode == 0:
            send_message({"device": device, "status": "command successful", "return": stdout})
            return stdout
        else:
            print(f"Command failed with return code {process.returncode}")
            send_message({"device": device, "status": "command error", "return": stderr})
            return stderr
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return None
# Sample commands
# {"action": "run", "command": "echo 'export MY_VARIABLE=\"my_value\"' >> /home/pir/.bashrc", "sudo": "False", "device": device}
# {"action": "run", "command": "sed -i 's/^export MY_VARIABLE=.*/export MY_VARIABLE=\"new_value\"/' /home/pir/.bashrc", "sudo": "False", "device": device}

# Callback when any publish is received
def on_publish_received(publish_packet_data):
    global idle
    publish_packet = publish_packet_data.publish_packet
    assert isinstance(publish_packet, mqtt5.PublishPacket)
    print("Received message from topic'{}':{}".format(publish_packet.topic, publish_packet.payload), flush=True)
    payload = publish_packet.payload
    payload_dict = json.loads(payload.decode())

    if 'test' in payload_dict:
        animations.print_colored_block(int(payload_dict['color'][0]), int(payload_dict['color'][1]), int(payload_dict['color'][2]))


    elif 'action' in payload_dict:
        #Something happened so set lamp back to normal animation and brightness
        strip.setBrightness(150)
        strip.show()
        animations.mode = 1

        if payload_dict['action'] == 'flux':
            animations.colorWipeReverse(strip, Color(int(payload_dict['color'][0]), int(payload_dict['color'][1]), int(payload_dict['color'][2])), 25)

        elif payload_dict['action'] == 'git' and payload_dict['status'] == 'start' and payload_dict['device'] == device:
            run_git_pull()

        elif payload_dict['action'] == 'run'  and payload_dict['device'] == device and 'command' in payload_dict:
            run_command(payload_dict['command'], payload_dict['sudo'])

        elif payload_dict['action'] == 'touch' and payload_dict['device'] == device:
            animations.colorWipeReverse(strip, Color(int(payload_dict['color'][0]), int(payload_dict['color'][1]),
                                             int(payload_dict['color'][2])), 25)
        elif payload_dict['action'] == 'touch' and payload_dict['device'] != device:
            animations.colorWipe(strip, Color(int(payload_dict['color'][0]), int(payload_dict['color'][1]),
                                      int(payload_dict['color'][2])), 25)
    idle = False


# Callback for the lifecycle event Stopped
def on_lifecycle_stopped(lifecycle_stopped_data: mqtt5.LifecycleStoppedData):
    print("Lifecycle Stopped", flush=True)
    global future_stopped
    future_stopped.set_result(lifecycle_stopped_data)


# Callback for the lifecycle event Connection Success
def on_lifecycle_connection_success(lifecycle_connect_success_data: mqtt5.LifecycleConnectSuccessData):
    print("Lifecycle Connection Success", flush=True)
    global future_connection_success
    future_connection_success.set_result(lifecycle_connect_success_data)


# Callback for the lifecycle event Connection Failure
def on_lifecycle_connection_failure(lifecycle_connection_failure: mqtt5.LifecycleConnectFailureData):
    print("Lifecycle Connection Failure", flush=True)
    print("Connection failed with exception:{}".format(lifecycle_connection_failure.exception), flush=True)


def send_message(message_to_send):
    message_topics= lamp_topic
    print("Publishing message to topic '{}': {}".format(message_topic, message_to_send), flush=True)
    json_str = json.dumps(message_to_send)
    publish_future = client.publish(mqtt5.PublishPacket(
        topic=message_topics,
        payload=json_str.encode(),
        qos=mqtt5.QoS.AT_LEAST_ONCE
    ))

def check_lamp_idle():
    global idle
    while True:
        if idle:
            print("Idle tracking started", flush=True)
            start_time = time.time()
            while idle:
                time_dif = time.time() - start_time
                if 1800 < time_dif <= 3600:
                    strip.setBrightness(100)
                    strip.show()
                elif 3600 < time_dif <= 5400:
                    strip.setBrightness(65)
                    strip.show()
                elif 5400 < time_dif <= 7200:
                    strip.setBrightness(30)
                    strip.show()
                elif 7200 < time_dif:
                    idle = False  # Set idle False to exit loops
                time.sleep(1)


if __name__ == '__main__':
    print("\nStarting Lamp\n", flush=True)
    message_count = 0
    message_topic = lamp_topic
    # Create the proxy options if the data is present in cmdData
    proxy_options = None
    if cmdData.input_proxy_host is not None and cmdData.input_proxy_port != 0:
        proxy_options = http.HttpProxyOptions(
            host_name=cmdData.input_proxy_host,
            port=cmdData.input_proxy_port)

    GPIO.setmode(GPIO.BCM)
    sensor_pin = 23
    GPIO.setup(sensor_pin, GPIO.IN)

    time_now = time.strftime('%Y-%m-%d %a %H:%M:%S %Z', time.localtime(time.time()))
    message_string = {'time': time_now, 'device': device, 'status': 'online'}

    idle_thread = threading.Thread(target=check_lamp_idle)
    idle_thread.daemon = True
    idle_thread.start()
    
    # Create NeoPixel object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Initialize the library (must be called once before other functions).
    strip.begin()

    GPIO.add_event_detect(sensor_pin, GPIO.RISING, callback=animations.tap_detected, bouncetime=200)

    # Create MQTT5 client
    client = mqtt5_client_builder.mtls_from_path(
        endpoint=cmdData.input_endpoint,
        port=cmdData.input_port,
        cert_filepath=cmdData.input_cert,
        pri_key_filepath=cmdData.input_key,
        ca_filepath=cmdData.input_ca,
        http_proxy_options=proxy_options,
        on_publish_received=on_publish_received,
        on_lifecycle_stopped=on_lifecycle_stopped,
        on_lifecycle_connection_success=on_lifecycle_connection_success,
        on_lifecycle_connection_failure=on_lifecycle_connection_failure,
        client_id=cmdData.input_clientId,
        session_expiry_interval_sec=90,
        clean_start=False,
        session_behavior=mqtt5.ClientSessionBehaviorType.REJOIN_POST_SUCCESS)
    print("MQTT5 Client Created", flush=True)

    if not cmdData.input_is_ci:
        print(f"Connecting to {cmdData.input_endpoint} with client ID '{cmdData.input_clientId}'...")
    else:
        print("Connecting to endpoint with client ID", flush=True)

    client.start()
    lifecycle_connect_success_data = future_connection_success.result(TIMEOUT)
    connack_packet = lifecycle_connect_success_data.connack_packet
    negotiated_settings = lifecycle_connect_success_data.negotiated_settings
    if not cmdData.input_is_ci:
        print(
            f"Connected to endpoint:'{cmdData.input_endpoint}' with Client ID:'{cmdData.input_clientId}' with reason_code:{repr(connack_packet.reason_code)}", flush=True)

    # Subscribe

    print("Subscribing to topic '{}'...".format(message_topic), flush=True)
    subscribe_future = client.subscribe(subscribe_packet=mqtt5.SubscribePacket(
        subscriptions=[mqtt5.Subscription(
            topic_filter=message_topic,
            qos=mqtt5.QoS.AT_LEAST_ONCE)]
    ))
    suback = subscribe_future.result(TIMEOUT)
    print("Subscribed with {}".format(suback.reason_codes), flush=True)

    if message_string:
        print("Sending messages until program killed", flush=True)

        publish_count = 1
        message = "{} [{}]".format(message_string, publish_count)
        print("Publishing message to topic '{}': {}".format(message_topic, message), flush=True)
        publish_future = client.publish(mqtt5.PublishPacket(
            topic=message_topic,
            payload=json.dumps(message_string),
            qos=mqtt5.QoS.AT_LEAST_ONCE
        ))
        publish_completion_data = publish_future.result(TIMEOUT)
        print("PubAck received with {}".format(repr(publish_completion_data.puback.reason_code)), flush=True)
        time.sleep(1)
        publish_count += 1
        color_spin = False

        animations.rainbow(strip) # Initialize LEDs with rainbow to show it's ready

        try:
            while True:
                idle = True
                #Wait for sensor touch
                if GPIO.input(sensor_pin):
                    print(f"gpio rising at: {time.time()}", flush=True)
                    idle = False
                    strip.setBrightness(150)
                    strip.show()
                    io_timer = 0

                    while GPIO.input(sensor_pin):
                        time.sleep(.5)
                        io_timer+=1

                        if io_timer == 2:
                            time_now = time.strftime('%Y-%m-%d %a %H:%M:%S %Z', time.localtime(time.time()))
                            send_message({"time": time_now, "device": device, "action": "touch", "color": my_color_rgb})
                            animations.mode = 1
                        elif io_timer >= 30:
                            GPIO.wait_for_edge(sensor_pin, GPIO.FALLING)
                            print("No touching", flush=True)
                            break
                        elif io_timer >= 10:
                            # Iterate over the generator and print RGB values
                            hues = animations.get_hues_of_color(my_color_rgb)
                            color_spin = True
                            for hue in hues:
                                print(f"Current hue: {hue}", flush=True)
                                animations.colorWipe(strip, hue, 5)
                                time.sleep(1.8)
                                if not GPIO.input(sensor_pin):
                                    break
                    time.sleep(1)
                    if animations.mode == 2:
                        #Enter White Mode
                        print("If mode 2 triggered", flush=True)
                        animations.colorWipe(strip, Color(250, 250, 250), 10)
                    elif animations.mode == 3:
                        #Enter rainbow mode
                        print("If mode 3 triggered", flush=True)    
                        animations.rainbowCycle(strip)

                    if color_spin:
                        flux_color = (r, g, b)
                        time_now = time.strftime('%Y-%m-%d %a %H:%M:%S %Z', time.localtime(time.time()))
                        send_message({"time": time_now, "device": device, "action": "flux", "color": flux_color})
                        color_spin = False

        except KeyboardInterrupt:
                print("\nProgram interrupted. Exiting...")
                animations.colorWipe(strip, Color(0, 0, 0), 10)
                GPIO.cleanup()
                idle = False
                idle_thread.join()

    # Unsubscribe
    print("Unsubscribing from topic '{}'".format(message_topic))
    unsubscribe_future = client.unsubscribe(unsubscribe_packet=mqtt5.UnsubscribePacket(
        topic_filters=[message_topic]))
    unsuback = unsubscribe_future.result(TIMEOUT)
    print("Unsubscribed with {}".format(unsuback.reason_codes))

    print("Stopping Client")
    client.stop()
    future_stopped.result(TIMEOUT)
    print("Client Stopped!")
    