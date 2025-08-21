from flask import Flask, request, Response
from PIL import Image
import requests
import io
import struct
import textwrap

app = Flask(__name__)

@app.route('/convert_and_generate_py', methods=['GET'])
def convert_and_generate_py():
    image_url = request.args.get('url')
    if not image_url:
        return "URL d'image manquante", 400

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(image_url, headers=headers)
        img = Image.open(io.BytesIO(response.content)).convert('RGB')
    except Exception as e:
        return f"Erreur lors de l'ouverture de l'image: {e}", 400

    width, height = img.size
    rgb_data = img.tobytes()

    lv_bytes = bytearray()
    for i in range(width * height):
        r = rgb_data[i*3]
        g = rgb_data[i*3 + 1]
        b = rgb_data[i*3 + 2]
        
        rgb565 = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
        lv_bytes.extend(struct.pack('<H', rgb565))

    # Convertit les octets en une chaîne hexadécimale échappée
    hex_str = ''.join(f'\\x{b:02X}' for b in lv_bytes)

    # Découpe la chaîne en lignes de 128 caractères et ajoute la syntaxe \
    line_length = 128
    wrapped_lines = textwrap.wrap(hex_str, width=line_length)
    wrapped_str = '\\\n'.join(wrapped_lines)

    py_code = f"""import lvgl as lv

TemporaryImage_data = b'{wrapped_str}'

TemporaryImage = lv.img_dsc_t({{
    'header': {{
        'always_zero': 0,
        'w': {width},
        'h': {height},
        'cf': lv.img.CF.TRUE_COLOR
    }},
    'data_size': len(TemporaryImage_data),
    'data': TemporaryImage_data
}})
"""

    return Response(
        py_code,
        mimetype="text/x-python",
        headers={"Content-Disposition": "attachment; filename=album_art.py"}
    )

if __name__ == '__main__':
    app.run()

