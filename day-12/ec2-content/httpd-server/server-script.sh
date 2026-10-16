
#!/bin/bash

set -e

# Update packages
sudo dnf update -y

# Install Apache HTTPD
sudo dnf install -y httpd

# Create a sample web page
echo "<h1>Hello from AWS EC2!</h1>" | sudo tee /var/www/html/index.html

# Start Apache and enable it at boot
sudo systemctl enable --now httpd

# Display service status
sudo systemctl status httpd --no-pager

echo "HTTPD server launched successfully!"
