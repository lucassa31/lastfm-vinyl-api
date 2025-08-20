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
        response = requests.get(image_url)
        img = Image.open(io.BytesIO(response.content)).resize((64, 64)).convert('RGBA')
    except Exception:
        return "Erreur lors de l'ouverture de l'image", 400

    width, height = img.size
    rgba_data = img.tobytes()

    # Format LVGL: CF.TRUE_COLOR_ALPHA = 32 bits ARGB (8 bits chacun)
    # On construit les octets dans l'ordre attendu
    py_bytes = bytearray()
    for i in range(width * height):
        r = rgba_data[i*4]
        g = rgba_data[i*4 + 1]
        b = rgba_data[i*4 + 2]
        a = rgba_data[i*4 + 3]
        py_bytes.extend([r, g, b, a])

    # Transformation en chaîne b'....'
    hex_str = ''.join(f'\\x{b:02X}' for b in py_bytes)

    # On découpe pour pas avoir une seule ligne immense
    wrapped = textwrap.fill(hex_str, width=64*4*4)  

    py_code = f"""import lvgl as lv

Image_data = b'{wrapped}'

Image = lv.img_dsc_t({{
    'header': {{
        'always_zero': 0,
        'w': {width},
        'h': {height},
        'cf': lv.img.CF.TRUE_COLOR_ALPHA
    }},
    'data_size': len(Image_data),
    'data': Image_data
}})
"""

    return Response(
        py_code,
        mimetype="text/x-python",
        headers={"Content-Disposition": "attachment; filename=album_art.py"}
    )


if __name__ == '__main__':
    app.run()
