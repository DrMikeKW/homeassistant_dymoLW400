#!/usr/bin/with-contenv bashio

# Load bashio
bashio::log.info "Starting Dymo LabelWriter 400 add-on..."

# Check if CUPS is running
if bashio::supervisor.ping; then
    bashio::log.info "Home Assistant Supervisor is running"
else
    bashio::log.error "Home Assistant Supervisor is not running"
    exit 1
fi

bashio::log.info "Setting up CUPS configuration..."

# Set up CUPS configuration
bashio::log.info "Setting up CUPS configuration..."
mkdir -p /run/cups
chmod 755 /run/cups

bashio::log.info "Starting CUPS service..."
cupsd

# Wait for CUPS to be fully initialized
bashio::log.info "Waiting for CUPS to be ready..."
while [ ! -e /run/cups/cups.sock ]; do
    sleep 1
done

# Additional wait to ensure CUPS is fully operational
sleep 1

# Debug USB devices
bashio::log.info "USB Devices:"
lsusb
bashio::log.info "USB Backend Information:"
lpinfo -v

# Try to detect DYMO printer
DYMO_URI=$(lpinfo -v | grep -i "dymo" | head -n 1 | awk '{print $2}')
bashio::log.info "Detected DYMO URI: $DYMO_URI"

if [ -n "$DYMO_URI" ]; then
    bashio::log.info "Found DYMO printer at $DYMO_URI"

    # Remove existing printer if it exists
    lpadmin -x dymo 2>/dev/null || true

    # Add the printer with direct USB access
    bashio::log.info "Adding DYMO printer..."
    lpadmin -p dymo -v "$DYMO_URI" -E -P /usr/share/cups/model/lw400.ppd

    # Set as default and accept jobs
    lpadmin -d dymo
    cupsenable dymo
    cupsaccept dymo

    # Set printer options
    lpoptions -p dymo -o PageSize=w167h288
else
    bashio::log.warning "No DYMO printer found!"
fi

# Show printer status
bashio::log.info "Printer Status:"
lpstat -t
lpstat -v

bashio::log.info "Starting Flask application..."
python3 /app.py