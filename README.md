This repo holds files necessary to run PiLamps, a friendship lamp that acts as a way to stay connected with loved ones. The lamp is an IoT device, running on a Raspberry Pi connected to a touch sensor and LED strip, and powered by AWS IoT Core and SNS.

There are various folders and files in this repo:
/ansible - WIP. For configuration of the RPi
/app - The actual application Python files
/config - WIP. For wifi configuration.
/packer - Packer .hcl to create a Docker image used with testing and CI pipeline
/terraform - Terraform files for creating IoT Core infrastructure

At this stage PiLamp is completely working, though I'd like to add a few new features (more on this below). My family and I use 3 lamps spread across the globe and have had no issues. With that said, there are some things to note:

    1. Price: Using AWS will have some fees, though unless you have dozens of devices, the total monthly costs should only be a few dollars (<$5)

    2. Physical Setup: There is a decent amount of manual setup required concerning the physical device (soldering and wiring skills. I've used RPi Zero through v4 devices to run PiLamps, along with ws2812x LEDs, a touch sensor, and shell to house everything. (This 3D printed lamp shell to be exact: https://www.thingiverse.com/thing:4129249)

    3. Digital Setup: The RPi's OS and wifi will need to be configured manually. Once you can ssh into the RPi you can then pull this repo to your device.

## How to setup

    1. Once you're able to ssh into your RPi, clone this repo to a directory

    2. Apply terraform/main.tf, changing variables as needed, to create an IoT Core device and policy. Note the Terraform outputs, the certificate and private key need to be placed in ~/certs, along with the CA file in /config.

    3. Add the environment variables:
        LAMP_NAME #This should be equal to Terraform's "thing_name" output
        LAMP_COLOR #This should be the name of a [CSS Matplotlib color](https://matplotlib.org/stable/gallery/color/named_colors.html#css-colors)
        LAMP_TOPIC #This should be equal to the Terraform "sns_topic" variable
        LAMP_ENDPOINT #This should be set to Terraform's "iot_endpoint" output

    4. Install the python libraries located in /docker/requirments.txt

    5. Start the program with a command similar to:
        sudo -E python3 ~/Git/aws_lamp/app/lamp/pi-lamp.py --endpoint $LAMP_ENDPOINT --ca_file ~/certs/AmazonRootCA1.pem --cert ~/certs/device.pem --key ~/certs/private.pem.key --client_id $LAMP_NAME --topic $LAMP_TOPIC --count 0

## Future Aditions

    1. More automation to reduce the above steps
    2. More testing (using docker)
    3. Add feature for when lamps touched at same time
