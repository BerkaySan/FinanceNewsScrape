#!/bin/bash

: '
    This script is used to set up the environment for the data collection process.
    It checks if Docker is installed and if not, installs it.
    It also checks if the firewall allows port 4444 and if not, allows it.
    Finally, it runs the Docker Compose file to start the data collection process.
     You used sudo docker compose up --build. As of Docker 19.03.0+, Docker Compose is integrated into the Docker command line interface (CLI) as a subcommand (docker-compose). Depending on your Docker version and setup, you might need to adjust this command:

    If you are using an older version of Docker without integrated Docker Compose, you might need to install Docker Compose separately and use sudo docker-compose up --build.
    If your Docker version is recent and includes Docker Compose as a part of the Docker CLI, the command you have used is correct. However, it is often integrated as docker compose (without the hyphen), not sudo docker compose. Ensure your Docker version supports this syntax.
'

# Check if Docker is installed
if ! command -v docker &> /dev/null
then
    echo "Docker bulunamadi. Yüklenmeye çalişiliyor..."

    # Update the package repository
    sudo apt-get update

    # Install required packages for Docker
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # Set up the stable repository
    echo \
        "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    sudo apt install docker-compose

    echo "Docker yüklendi."
else
    echo "Docker çoktan yüklü."
fi

if ! sudo ufw status | grep --quiet "4444"
then
    echo "4444 numarali bağlanti noktasina izin verilmiyor. İzin vermeye çalişiliyor..."

    sudo ufw allow 4444
else
    echo "4444 numarali bağlanti noktasina çoktan izin verildi."
fi

# Infinite loop to keep the script running
while true; do
    # Execute your command or script
    echo "Veri çekme işlemine başlaniyor..."

    sudo docker compose up --build

    echo "Veri çekme işlemi tamamlandi."

    sleep 10800
done