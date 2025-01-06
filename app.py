from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import subprocess
import tempfile
import os

app = Flask(__name__)

LABEL_SIZES = {
    'standard_address': {'width': 425, 'height': 1051, 'media': 'w79h252' },
    'multi_purpose': {'width': 673, 'height': 378, 'media': 'w162h90' },
}

def create_label(label_type, orientation, title, subtitle):
    dimensions = LABEL_SIZES[label_type]
    width, height = dimensions['width'], dimensions['height']

    if orientation == 'landscape':
        width, height = height, width  # Swap dimensions for landscape

    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    padding = 20
    available_width = width - (2 * padding)
    available_height = height - (2 * padding)

    def get_font_size(text, max_width, max_height, is_title=True):
        font_size = 200 if is_title else 100
        while font_size > 8:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            if text_width <= max_width and text_height <= (max_height / 2):
                return font_size, font, text_width, text_height
            font_size -= 2
        return font_size, ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)

    title_font_size, title_font, title_width, title_height = get_font_size(title, available_width, available_height, True)
    subtitle_font_size, subtitle_font, subtitle_width, subtitle_height = get_font_size(subtitle, available_width, available_height, False)

    title_x = (width - title_width) // 2
    subtitle_x = (width - subtitle_width) // 2
    total_height = title_height + subtitle_height
    start_y = (height - total_height) // 2

    draw.text((title_x, start_y), title, fill='black', font=title_font)
    draw.text((subtitle_x, start_y + title_height + 20), subtitle, fill='black', font=subtitle_font)

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

        label = create_label(label_type, orientation, title, subtitle)

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            label.save(tmp.name, 'PNG')
            tmp_path = tmp.name

        page_size = LABEL_SIZES[label_type]['media']

        cmd = ['lpr', '-P', 'dymo', '-o', f'PageSize={page_size}', tmp_path]
        subprocess.run(cmd, check=True)

        os.unlink(tmp_path)

        return jsonify({'status': 'success', 'message': 'Label printed successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)