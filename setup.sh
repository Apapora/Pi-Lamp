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
cur_dir=$(pwd)

read -p "WARNING: Please be sure to update variables.tf (or use a .tfvars file) with your values. (Hit enter to continue)"

# Step 2: Check python requirments
python3 --version || {
    echo "Please install python and pip."
    exit 1
}

# List of Python packages to check
packages=("rpi_ws281x" "RPi.GPIO" "boto3" "awsiotsdk" "awsiot" "matplotlib")
missing_packages=()

function check_pip_package {
    local package_name="$1"

    if pip show "$package_name" &>/dev/null; then
        # Package installed. Let them know
        echo "$package_name is installed."
    else
        # Package does not exist
        missing_packages+=("$package_name")
    fi
}

# Iterate through the list of packages
for package in "${packages[@]}"; do
    check_pip_package "$package"
done

# Check if any packages are missing and provide a summary
if [ ${#missing_packages[@]} -eq 0 ]; then
    echo "All required packages are installed."
else
    echo "The following packages are not installed: ${missing_packages[*]}"
    echo "Please install them and restart this setup"
    exit 1
fi

# Step 3: Terraform init and terraform apply without auto-approve, redirecting input from /dev/null
cd ./terraform
git checkout dev
terraform init
wait $!

# Set the account_id variable for Terraform using AWS CLI
TF_VAR_account_id=$(aws sts get-caller-identity --query 'Account' --output text)
export TF_VAR_account_id

terraform apply -var="account_id=$TF_VAR_account_id" </dev/null &
wait $!

# Step 4: Create and organize certs
mkdir ~/certs
terraform output device_private_key >~/certs/private.key || {
    echo "Issues with getting private key output. Exiting.." && exit 1
}
terraform output device_certificate_pem >~/certs/cert.pem || {
    echo "Issues with getting the certificate output. Exiting.." && exit 1
}
mv ./config/AmazonRootCA1.pem ~/certs/AmazonRootCA1.pem

# Step 5: Prompt user for LAMP_TOPIC and LAMP_COLOR
read -p "Enter the value for your lamp color (ie: 'red'): " LAMP_COLOR
read -p "Enter the value you used for your lamp topic (ie: 'lamp/test')" LAMP_TOPIC

# Step 6: Get the iot_endpoint output from Terraform
LAMP_ENDPOINT=$(terraform output iot_endpoint)
LAMP_NAME=$(terraform output thing_name)

# Step 7: Set environment variables to ~/.bashrc
function set_bashrc_variable {
    local variable_name="$1"
    local variable_value="$2"

    if grep -q "^export $variable_name=" ~/.bashrc; then
        # Variable already exists, update its value
        sed -i "s/^export $variable_name=.*/export $variable_name='$variable_value'/" ~/.bashrc
    else
        # Variable does not exist, append it
        echo "export $variable_name='$variable_value'" >>~/.bashrc
    fi
}

set_bashrc_variable "LAMP_NAME" "$LAMP_NAME"
set_bashrc_variable "LAMP_COLOR" "$LAMP_COLOR"
set_bashrc_variable "LAMP_TOPIC" "$LAMP_TOPIC"
set_bashrc_variable "LAMP_ENDPOINT" "$LAMP_ENDPOINT"
echo "Variables added to ~/.bashrc"

# Final message
echo "Script completed successfuly. You can now start the lamp with a command similar to:"
echo "sudo -E python3 ./Pi-Lamp/app/pi-lamp.py --endpoint \$LAMP_ENDPOINT --ca_file ~/certs/AmazonRootCA1.pem --cert ~/certs/cert.pem --key ~/certs/private.key --client_id \$LAMP_NAME --topic \$LAMP_TOPIC --count 0"
