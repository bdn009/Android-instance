#!/bin/bash
# ──────────────────────────────────────────────────────────
# CloudRoid — Host Setup Script
# Run on Ubuntu 24.04 LTS to configure Waydroid support
# ──────────────────────────────────────────────────────────

set -e

echo "╔══════════════════════════════════════════════════╗"
echo "║       CloudRoid Host Setup — Ubuntu 24.04        ║"
echo "╚══════════════════════════════════════════════════╝"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root: sudo bash setup.sh"
    exit 1
fi

echo ""
echo "▶ Step 1: System Update"
apt-get update && apt-get upgrade -y

echo ""
echo "▶ Step 2: Install Dependencies"
apt-get install -y \
    curl \
    wget \
    lxc \
    android-tools-adb \
    python3-pip \
    linux-modules-extra-$(uname -r)

echo ""
echo "▶ Step 2.5: Install Docker"
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

echo ""
echo "▶ Step 3: Install Waydroid"
# Add Waydroid repository securely (modern apt approach)
mkdir -p /etc/apt/keyrings
curl --retry 3 --retry-all-errors -fsSL https://repo.waydroid.org/waydroid.gpg | sudo gpg --dearmor --yes -o /etc/apt/keyrings/waydroid.gpg
echo "deb [signed-by=/etc/apt/keyrings/waydroid.gpg] https://repo.waydroid.org/ubuntu jammy main" > /etc/apt/sources.list.d/waydroid.list
apt-get update
apt-get install -y waydroid

echo ""
echo "▶ Step 4: Initialize Waydroid"
waydroid init -s GAPPS

echo ""
echo "▶ Step 5: Load Required Kernel Modules"
modprobe binder_linux
modprobe ashmem_linux 2>/dev/null || true

# Persist modules across reboots
echo "binder_linux" >> /etc/modules-load.d/waydroid.conf
echo "ashmem_linux" >> /etc/modules-load.d/waydroid.conf

echo ""
echo "▶ Step 6: Configure Docker"
systemctl enable docker
systemctl start docker

# Add current user to docker group
if [ -n "$SUDO_USER" ]; then
    usermod -aG docker "$SUDO_USER"
fi

echo ""
echo "▶ Step 7: Create Directories"
mkdir -p /opt/cloudroid/uploads/apks
mkdir -p /opt/cloudroid/logs

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║                ✅ Setup Complete!                ║"
echo "║                                                  ║"
echo "║  Next steps:                                     ║"
echo "║  1. Reboot the server                            ║"
echo "║  2. cd /path/to/project                          ║"
echo "║  3. docker compose up -d                         ║"
echo "╚══════════════════════════════════════════════════╝"
