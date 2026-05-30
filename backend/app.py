import os
from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
import io
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Simple image composer: creates a 1000x1000 background and overlays the provided quote.
@app.route('/compose', methods=['POST'])
def compose():
    data = request.json or {}
    quote = data.get('quote', 'Life is what happens when you\'re busy making other plans.')
    author = data.get('author', '')
    bg_color = data.get('bg_color', '#ffffff')

    img = Image.new('RGB', (1000, 1000), bg_color)
    draw = ImageDraw.Draw(img)

    # Basic font handling - expects a TTF in project or system fonts
    try:
        font = ImageFont.truetype('arial.ttf', 48)
    except Exception:
        font = ImageFont.load_default()

    text = f"\"{quote}\"\n\n{author}" if author else f"\"{quote}\""
    w, h = draw.multiline_textsize(text, font=font)
    draw.multiline_text(((1000-w)/2, (1000-h)/2), text, fill='black', font=font, align='center')

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

# Endpoint to POST to Pinterest - placeholder that demonstrates the expected payload.
@app.route('/post_pin', methods=['POST'])
def post_pin():
    data = request.json or {}
    image_url = data.get('image_url')  # could be an uploaded image URL or local upload workflow
    board_id = os.getenv('PINTEREST_BOARD_ID')
    access_token = os.getenv('PINTEREST_ACCESS_TOKEN')

    if not access_token or not board_id:
        return jsonify({'error': 'PINTEREST_ACCESS_TOKEN and PINTEREST_BOARD_ID must be set in env'}), 400

    # Pinterest API integration would go here. For safety, this prototype does not attempt
    # to call the API without explicit user-provided tokens and consent.
    # Example (pseudo):
    # resp = requests.post('https://api.pinterest.com/v5/pins', headers={...}, json={...})

    return jsonify({
        'status': 'ready',
        'note': 'Constructed payload; implement API call after OAuth and consent is configured.',
        'board_id': board_id,
        'image_url': image_url
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
