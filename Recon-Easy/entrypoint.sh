#!/bin/bash

# Entrypoint script for the Apache CTF container

# Ensure the script exits if any command fails
set -e

# Path to the certificate generation script
CERT_GEN_SCRIPT="/usr/local/apache2/conf/certs/generate_cert.sh"

echo "Container entrypoint started."

# --- Generate Certificate ---
echo "Running certificate generation script..."
bash "$CERT_GEN_SCRIPT"
echo "Certificate generation script finished."

# --- Start Apache ---
echo "Starting Apache HTTP Server in foreground..."

# Execute the default CMD (httpd-foreground) passed from the Dockerfile
exec "$@"
