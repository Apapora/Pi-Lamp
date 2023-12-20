#!/bin/bash

# Step 1: Check if AWS is configured
if ! aws --version &>/dev/null; then
    echo "AWS CLI is not configured. Please run 'aws configure' to set up your AWS credentials before running this script."
    exit 1
fi

if ! terraform --version &>/dev/null; then
    echo "Terraform is not installed. Please install and configure before running this script."
    exit 1
fi

# Step 1.5: Git clone the repo into the home folder
cd ~
rm -rf Pi-Lamp || {
    git clone https://github.com/Apapora/Pi-Lamp.git || {
        echo "Issues with cloning the repo. Exiting.." && exit 1
    }
}

read -p "WARNING: Please be sure to update variables.tf (or use a .tfvars file) with your values. (Hit enter for OK)"

# Step 2: Change directory to the Terraform folder and collect TF variables
cd ~/Pi-Lamp/terraform
git checkout dev

# Step 3: Terraform init and terraform apply without auto-approve, redirecting input from /dev/null
terraform init
wait $!
terraform apply </dev/null &

# Wait for the terraform apply command to finish
wait $!

# Step 4: Get the private_key output from Terraform and save it to private.key
terraform output device_private_key >~/certs/private.key || {
    echo "Issues with getting private key output. Exiting.." && exit 1
}
terraform output device_certificate_pem >~/certs/cert.pem || {
    echo "Issues with getting the certificate output. Exiting.." && exit 1
}

# Step 5: Prompt user for LAMP_TOPIC and LAMP_COLOR
read -p "Enter the value you used for your lamp topic" LAMP_TOPIC
read -p "Enter the value for your lamp color: " LAMP_COLOR

# Step 6: Get the iot_endpoint output from Terraform
LAMP_ENDPOINT=$(terraform output iot_endpoint)
LAMP_NAME=$(terraform output thing_name)

# Step 7: Set environment variables to ~/.bashrc
echo "export LAMP_NAME: '$LAMP_NAME'" >>~/.bashrc
echo "export LAMP_COLOR: '$LAMP_COLOR'" >>~/.bashrc
echo "export LAMP_TOPIC: '$LAMP_TOPIC'" >>~/.bashrc
echo "export LAMP_ENDPOINT: '$LAMP_ENDPOINT'" >>~/.bashrc
