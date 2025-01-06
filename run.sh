#!/usr/bin/with-contenv bashio

# Set up CUPS configuration
bashio::log.info "Setting up CUPS configuration..."
mkdir -p /run/cups
chmod 755 /run/cups

mkdir -p /usr/share/cups/model
cp /tmp/dymo-cups-drivers-1.4.0.5/ppd/lw400.ppd /usr/share/cups/model/

bashio::log.info "Starting CUPS service..."
cupsd

# Wait for CUPS to be fully initialized
bashio::log.info "Waiting for CUPS to be ready..."
while [ ! -e /run/cups/cups.sock ]; do
    sleep 1
done

# Additional wait to ensure CUPS is fully operational
sleep 1

## Get DYMO URI
#DYMO_URI=$(lpinfo -v | grep -i "dymo" | head -n 1 | awk '{print $2}')
#bashio::log.info "Found DYMO URI: $DYMO_URI"
#
#if [ -z "$DYMO_URI" ]; then
#    bashio::log.error "No DYMO printer found!"
#    exit 1
#fi
#
## Remove existing printer if it exists
#bashio::log.info "Removing all existing printer configurations..."
#lpstat -p | awk '{print $2}' | xargs -I {} lpadmin -x {} 2>/dev/null || true
#
## Add the printer with the PPD file
#bashio::log.info "Adding DYMO printer to CUPS..."
#lpadmin -p dymo -v "$DYMO_URI" -P /usr/share/cups/model/lw400.ppd
##lpadmin -p dymo -v usb://DYMO/LabelWriter%20450?serial=01010112345600 -P /usr/share/cups/model/lw450.ppd
#
#cupsenable dymo
#cupsaccept dymo
#lpoptions -d dymo
#
#bashio::log.info "DYMO printer setup completed"
#lpstat -p dymo -l
#
## Debug commands to add at the end of run.sh before python3 /app.py
#bashio::log.info "Testing printer connection..."
#lpstat -t
#lpstat -v
#lpstat -p dymo -l
#lpoptions -p dymo -l
#
#bashio::log.info "Starting Flask application..."
python3 /app.py