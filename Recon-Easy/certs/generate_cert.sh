#!/bin/bash

# Script to generate a self-signed certificate and private key
# using the provided OpenSSL configuration file.

# Ensure the script exits if any command fails
set -e

# --- Configuration ---
CERT_DIR="/usr/local/apache2/conf/certs"
KEY_FILE="${CERT_DIR}/server.key"
CSR_FILE="${CERT_DIR}/server.csr" # Certificate Signing Request (intermediate)
CRT_FILE="${CERT_DIR}/server.crt"
CONF_FILE="${CERT_DIR}/openssl.cnf"
DAYS_VALID=365 # Validity period for the certificate

# --- Certificate Generation ---

echo "Generating private key and certificate..."

# Check if certificate and key already exist; if so, skip generation
if [ -f "$CRT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "Certificate and key already exist. Skipping generation."
    exit 0
fi

# Generate the private key (if it doesn't exist)
if [ ! -f "$KEY_FILE" ]; then
    openssl genpkey -algorithm RSA -out "$KEY_FILE" -pkeyopt rsa_keygen_bits:2048
    echo "Private key generated: $KEY_FILE"
else
    echo "Private key already exists."
fi

# Generate the Certificate Signing Request (CSR) using the config file
openssl req -new -key "$KEY_FILE" -out "$CSR_FILE" -config "$CONF_FILE"
echo "CSR generated: $CSR_FILE"

# Generate the self-signed certificate using the CSR, private key, and config file (for extensions)
openssl x509 -req -days "$DAYS_VALID" -in "$CSR_FILE" -signkey "$KEY_FILE" -out "$CRT_FILE" -extensions req_ext -extfile "$CONF_FILE"
echo "Self-signed certificate generated: $CRT_FILE"

# Clean up the CSR file (no longer needed)
rm "$CSR_FILE"

# Set appropriate permissions for the private key (readable only by root/owner)
chmod 600 "$KEY_FILE"

echo "Certificate generation complete."
