from flask import Flask, request, jsonify
import subprocess
import logging
import os
import time
import re

logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_detailed_printer_status():
    """Get detailed printer status including queue and driver info"""
    status_info = {}

    try:
        # Check printer existence and basic status
        lpstat_result = subprocess.run(
            ['lpstat', '-v', 'dymo'],
            capture_output=True,
            text=True
        )
        status_info['device_status'] = lpstat_result.stdout.strip()

        # Get printer state
        lpstat_p_result = subprocess.run(
            ['lpstat', '-p', 'dymo', '-l'],
            capture_output=True,
            text=True
        )
        status_info['printer_state'] = lpstat_p_result.stdout.strip()

        # Get queue status
        lpq_result = subprocess.run(
            ['lpq', '-P', 'dymo'],
            capture_output=True,
            text=True
        )
        status_info['queue_status'] = lpq_result.stdout.strip()

        # Get printer options
        lpoptions_result = subprocess.run(
            ['lpoptions', '-p', 'dymo', '-l'],
            capture_output=True,
            text=True
        )
        status_info['printer_options'] = lpoptions_result.stdout.strip()

        logger.debug(f"Detailed printer status: {status_info}")
        return status_info

    except Exception as e:
        logger.error(f"Error getting detailed printer status: {str(e)}")
        return None

def check_printer_status():
    """Enhanced printer status check"""
    try:
        detailed_status = get_detailed_printer_status()
        if not detailed_status:
            return False

        # Check if printer is accepting jobs
        accept_check = subprocess.run(
            ['cupsaccept', '-h', 'localhost', 'dymo'],
            capture_output=True,
            text=True
        )

        # Check if printer is enabled
        enable_check = subprocess.run(
            ['cupsenable', 'dymo'],
            capture_output=True,
            text=True
        )

        return (
            detailed_status.get('device_status') and
            'error' not in detailed_status.get('printer_state', '').lower() and
            accept_check.returncode == 0 and
            enable_check.returncode == 0
        )
    except Exception as e:
        logger.error(f"Error in printer status check: {str(e)}")
        return False

def get_print_job_status(job_id):
    """Enhanced print job status check"""
    try:
        # Check job status using lpstat
        lpstat_result = subprocess.run(
            ['lpstat', '-o', 'dymo'],  # Changed to use -o flag for job listing
            capture_output=True,
            text=True
        )

        # Check queue status
        lpq_result = subprocess.run(
            ['lpq', '-P', 'dymo'],  # Removed job_id parameter
            capture_output=True,
            text=True
        )

        status = {
            'lpstat_output': lpstat_result.stdout,
            'lpq_output': lpq_result.stdout,
            'error_output': lpstat_result.stderr or lpq_result.stderr
        }

        logger.debug(f"Job {job_id} detailed status: {status}")
        return status

    except Exception as e:
        logger.error(f"Error checking job status: {str(e)}")
        return None

@app.route('/print', methods=['GET'])
def print_label():
    """Enhanced print endpoint with better error handling and status checking"""
    text = request.args.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    logger.info(f"Print request received for text: {text}")

    # Get detailed printer status before printing
    printer_status = get_detailed_printer_status()
    if not printer_status:
        return jsonify({'error': 'Unable to get printer status'}), 500

    logger.info(f"Current printer status: {printer_status}")

    if not check_printer_status():
        return jsonify({
            'error': 'Printer not ready',
            'details': printer_status
        }), 500

    try:
        # Create temporary file with unique name
        temp_file = f'/tmp/label_{int(time.time())}.txt'
        with open(temp_file, 'w') as f:
            f.write(text)

        # Enhanced print command with more options
        cmd = [
            'lp',
            '-d', 'dymo',
            '-o', 'media=w162h90',
            '-o', 'raw',  # Try raw mode for direct printing
            '-o', 'print-quality=5',  # High quality
            temp_file
        ]

        logger.debug(f"Executing print command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)

        if result.returncode == 0:
            # Extract job ID from lp output
            job_id_match = re.search(r'-\d+', result.stdout)
            if not job_id_match:
                return jsonify({'error': 'Could not determine job ID'}), 500

            job_id = job_id_match.group()
            logger.info(f"Print job submitted successfully with ID: {job_id}")

            # Wait a moment for the print job to process
            time.sleep(2)

            # Check if job is still in queue
            job_status = get_print_job_status(job_id)

            # If we can't find the job in queue, assume it completed
            if "dymo is ready" in job_status.get('lpq_output', '').lower():
                return jsonify({
                    'status': 'success',
                    'job_id': job_id,
                    'message': 'Print job completed',
                    'details': job_status
                })

            # If we see specific error messages, report failure
            if any(error in str(job_status).lower() for error in ['error', 'failed', 'canceled']):
                return jsonify({
                    'error': 'Print job failed',
                    'job_id': job_id,
                    'status': job_status
                }), 500

                attempt += 1
                time.sleep(2)  # Increased wait time between checks

            return jsonify({
                'status': 'submitted',
                'job_id': job_id,
                'message': 'Print job submitted but completion status unknown',
                'last_known_status': job_status
            })
        else:
            error_msg = result.stderr or "Unknown error occurred"
            logger.error(f"Print command failed: {error_msg}")
            return jsonify({
                'error': error_msg,
                'command_output': result.stdout,
                'printer_status': printer_status
            }), 500

    except Exception as e:
        logger.error(f"Error printing label: {str(e)}")
        return jsonify({
            'error': str(e),
            'printer_status': printer_status
        }), 500

@app.route('/status', methods=['GET'])
def printer_status():
    """Enhanced status endpoint with detailed printer information"""
    detailed_status = get_detailed_printer_status()
    if not detailed_status:
        return jsonify({
            'status': 'error',
            'message': 'Unable to get printer status'
        }), 503

    is_ready = check_printer_status()
    return jsonify({
        'status': 'ready' if is_ready else 'not ready',
        'details': detailed_status
    })

if __name__ == '__main__':
    # Initial printer check on startup
    logger.info("Checking printer status on startup...")
    initial_status = get_detailed_printer_status()
    logger.info(f"Initial printer status: {initial_status}")

    app.run(host='0.0.0.0', port=8000)