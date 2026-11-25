#!/bin/bash
# Script d'installation (Partie 7 de l'exercice Git)
set -e

echo "Starting installation..."
sudo apt update
sudo apt install -y git
echo "Installation complete!"
