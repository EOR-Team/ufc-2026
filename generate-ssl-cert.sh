#!/bin/bash
# Generate self-signed SSL certificate for nginx HTTPS configuration
# Required for cross-origin microphone access in browsers
#
# IMPORTANT: This script uses sudo, which changes $HOME to /root
#            You MUST edit line 14 below to use your actual home directory path
#            Example: SSL_DIR="/home/yourusername/ssl"

set -e

echo "Generating self-signed SSL certificate for HTTPS..."
echo "This certificate will be valid for 365 days."

# Create SSL directory if it doesn't exist
# IMPORTANT: Replace /home/n1ghts4kura with your actual home directory path
SSL_DIR="/home/n1ghts4kura/ssl"
if [ ! -d "$SSL_DIR" ]; then
    echo "Creating SSL directory: $SSL_DIR"
    sudo mkdir -p "$SSL_DIR"
    sudo chmod 700 "$SSL_DIR"
fi

# Generate private key and certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$SSL_DIR/selfsigned.key" \
    -out "$SSL_DIR/selfsigned.crt" \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=UFC-2026/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:0.0.0.0"

# Set appropriate permissions
sudo chmod 600 "$SSL_DIR/selfsigned.key"
sudo chmod 644 "$SSL_DIR/selfsigned.crt"

echo ""
echo "SSL certificate generated successfully!"
echo "Key file: $SSL_DIR/selfsigned.key"
echo "Cert file: $SSL_DIR/selfsigned.crt"
echo ""
echo "You can now start nginx with: sudo nginx -c /path/to/nginx.conf"
echo ""
echo "Note: Browsers will show a security warning for self-signed certificates."
echo "You need to accept the warning to proceed with microphone access."
