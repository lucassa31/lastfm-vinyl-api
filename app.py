from flask import Flask, request, Response
from PIL import Image
import requests
import io
import textwrap

app = Flask(__name__)

@app.route('/convert_and_generate_py', methods=['GET'])
def convert_and_generate_py():
    image_url = request.args.get('url')
    if not image_url:
        return "URL d'image manquante", 400

    try:
        response = requests.get(image_url)
        img = Image.open(io.BytesIO(response.content)).convert('RGBA')
    except Exception:
        return "Erreur lors de l'ouverture de l'image", 400

    width, height = img.size
    rgba_data = img.tobytes()

    # LVGL attend ARGB
    lv_bytes = bytearray()
    for i in range(width * height):
        r = rgba_data[i*4]
        g = rgba_data[i*4 + 1]
        b = rgba_data[i*4 + 2]
        a = rgba_data[i*4 + 3]
        lv_bytes.extend([a, r, g, b])

    # Conversion en chaîne hexadécimale
    hex_str = ''.join(f'\\x{b:02X}' for b in lv_bytes)
    # Découpage en lignes pour ressembler à ui.ipages
    wrapped = textwrap.fill(hex_str, width=64*4)  

    py_code = f"""import lvgl as lv

TemporaryImage_data = b'{wrapped}'

TemporaryImage = lv.img_dsc_t({{
    'header': {{
        'always_zero': 0,
        'w': {width},
        'h': {height},
        'cf': lv.img.CF.TRUE_COLOR_ALPHA
    }},
    'data_size': len(TemporaryImage_data),
    'data': TemporaryImage_data
}})

TemporaryImageArray = [TemporaryImage, TemporaryImage]
"""

    return Response(
        py_code,
        mimetype="text/x-python",
        headers={"Content-Disposition": "attachment; filename=album_art.py"}
    )

if __name__ == '__main__':
    app.run()
