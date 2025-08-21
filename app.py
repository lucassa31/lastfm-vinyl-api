from flask import Flask, request, Response
from PIL import Image
import requests
import io
import textwrap
import struct

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
        
        # Conversion de l'image en RGB (sans canal alpha)
        img = Image.open(io.BytesIO(response.content)).convert('RGB')
    except Exception as e:
        return f"Erreur lors de l'ouverture de l'image: {e}", 400

    width, height = img.size
    rgb_data = img.tobytes()

    # Conversion de chaque pixel RGB (3 octets) en RGB565 (2 octets)
    lv_bytes = bytearray()
    for i in range(width * height):
        r = rgb_data[i*3]
        g = rgb_data[i*3 + 1]
        b = rgb_data[i*3 + 2]

        # Formule de conversion RGB888 vers RGB565
        # R (5 bits) = (r / 255) * 31 << 11
        # G (6 bits) = (g / 255) * 63 << 5
        # B (5 bits) = (b / 255) * 31
        
        rgb565 = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
        
        # Emballe les 2 octets du pixel RGB565 en little-endian
        lv_bytes.extend(struct.pack('<H', rgb565))

    # Conversion en chaîne hexadécimale
    hex_str = ''.join(f'\\x{b:02X}' for b in lv_bytes)
    # Découpage en lignes
    wrapped = textwrap.fill(hex_str, width=64*4)

    py_code = f"""import lvgl as lv

TemporaryImage_data = b'{wrapped}'

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
