from flask import Flask, request, Response
from PIL import Image
import requests
import io

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

    # LVGL: CF.TRUE_COLOR_ALPHA = 32 bits ARGB
    py_bytes = bytearray()
    for i in range(width * height):
        r = rgba_data[i*4]
        g = rgba_data[i*4 + 1]
        b = rgba_data[i*4 + 2]
        a = rgba_data[i*4 + 3]
        # LVGL attend l'ordre ARGB
        py_bytes.extend([a, r, g, b])

    # On écrit directement comme bytes, pas de chaîne avec \x
    py_code = f"""import lvgl as lv

Image_data = {list(py_bytes)}

Image = lv.img_dsc_t({{
    'header': {{
        'always_zero': 0,
        'w': {width},
        'h': {height},
        'cf': lv.img.CF.TRUE_COLOR_ALPHA
    }},
    'data_size': len(Image_data),
    'data': bytes(Image_data)
}})
"""

    return Response(
        py_code,
        mimetype="text/x-python",
        headers={"Content-Disposition": "attachment; filename=album_art.py"}
    )

if __name__ == '__main__':
    app.run()
