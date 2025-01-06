from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import subprocess
import tempfile
import os

app = Flask(__name__)

# Label size configurations (in pixels, assuming 300 DPI)
LABEL_SIZES = {
    'standard_address': {'width': 1960, 'height': 3384},  # w167h288
    'other_address': {'width': 1180, 'height': 236}      # w100h20
}

def create_label(label_type, orientation, title, subtitle):
    # Get label dimensions
    dimensions = LABEL_SIZES[label_type]
    width = dimensions['width']
    height = dimensions['height']

    # Create new image with white background
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # Calculate available space for text
    padding = 20  # pixels
    available_width = width - (2 * padding)
    available_height = height - (2 * padding)

    # Start with a large font size and scale down until it fits
    def get_font_size(text, max_width, max_height, is_title=True):
        font_size = 200 if is_title else 100  # Start with large size
        while font_size > 8:  # Minimum readable size
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            text_width, text_height = draw.textsize(text, font=font)
            if text_width <= max_width and text_height <= (max_height / 2):
                return font_size, font
            font_size -= 2
        return font_size, ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)

    # Get appropriate font sizes
    title_font_size, title_font = get_font_size(title, available_width, available_height, True)
    subtitle_font_size, subtitle_font = get_font_size(subtitle, available_width, available_height, False)

    # Calculate text dimensions
    title_width, title_height = draw.textsize(title, font=title_font)
    subtitle_width, subtitle_height = draw.textsize(subtitle, font=subtitle_font)

    # Calculate positions to center the text
    title_x = (width - title_width) // 2
    subtitle_x = (width - subtitle_width) // 2

    total_height = title_height + subtitle_height
    start_y = (height - total_height) // 2

    # Draw the text
    draw.text((title_x, start_y), title, fill='black', font=title_font)
    draw.text((subtitle_x, start_y + title_height + 10), subtitle, fill='black', font=subtitle_font)

    # Rotate if needed
    if orientation == 'landscape':
        image = image.rotate(90, expand=True)

    return image

@app.route('/print_label', methods=['POST'])
def print_label():
    try:
        data = request.json
        label_type = data.get('label_type', 'standard_address')
        orientation = data.get('orientation', 'portrait')
        title = data.get('title', '')
        subtitle = data.get('subtitle', '')

        if not title:
            return jsonify({'error': 'Title is required'}), 400

        # Create the label image
        label = create_label(label_type, orientation, title, subtitle)

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            label.save(tmp.name, 'PNG')
            tmp_path = tmp.name

        # Determine page size based on label type
        page_size = 'w167h288' if label_type == 'standard_address' else 'w100h20'

        # Print using lpr
        cmd = ['lpr', '-P', 'dymo', '-o', f'PageSize={page_size}', tmp_path]
        subprocess.run(cmd, check=True)

        # Clean up temporary file
        os.unlink(tmp_path)

        return jsonify({'status': 'success', 'message': 'Label printed successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)