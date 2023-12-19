packer {
  required_plugins {
    docker = {
      version = ">= 1.0.1"
      source  = "github.com/hashicorp/docker"
    }
  }
}

source "docker" "python" {
  image      = "python:3"
  pull       = true
  commit     = true
  changes = [
    "ENTRYPOINT [\"\"]",
    "CMD [\"\"]"
  ]
}

build {
  name = "lamp-img"
  sources = [
    "source.docker.python"
  ]
  provisioner "shell" {
    environment_vars = [
      "FOO=hello world",
    ]
    inline = [
      "echo Adding file to Docker Container",
      "echo \"FOO is $FOO\" > example.txt",
      "apt-get update",
      "apt-get install -y unzip",
      "curl -O https://releases.hashicorp.com/terraform/1.6.5/terraform_1.6.5_linux_amd64.zip",
      "unzip terraform_1.6.5_linux_amd64.zip -d /usr/local/bin/",
      "curl -O https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip",
      "unzip awscli-exe-linux-x86_64.zip",
      "./aws/install",
      "apt-get install -y python3-pip iputils-ping",
      "python -m venv ~/venv",
      ". ~/venv/bin/activate",
      "pip install --upgrade pip",
      "pip install rpi-ws281x RPi.GPIO boto3 awsiotsdk awscrt awsiot",
      "mkdir -p ~/certs"
    ]
  }

  post-processor "docker-tag" {
    repository = "pilamp"
    tags       = ["python-lamp"]
    only       = ["docker.python"]
  }
}
