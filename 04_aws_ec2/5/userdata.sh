#!/bin/bash

apt update
apt install -y docker.io

systemctl enable docker
systemctl start docker

docker run -d \
  --name app \
  --restart unless-stopped \
  -p 80:80 \
  nginx
