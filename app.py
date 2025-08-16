from flask import Flask, request, Response
from PIL import Image
import requests
import io
import struct
import base64

app = Flask(__name__)

@app.route('/convert_and_stream', methods=['GET'])
def convert_and_stream():
    image_url = request.args.get('url')
    if not image_url:
        return "URL d'image manquante", 400

    try:
        response = requests.get(image_url)
        img = Image.open(io.BytesIO(response.content)).resize((240, 240)).convert('RGB')
    except Exception:
        return "Erreur lors de l'ouverture de l'image", 400

    # Conversion RGB -> RGB565
    width, height = img.size
    rgb_data = img.tobytes()
    rgb565_data = bytearray(width * height * 2)

    for i in range(width * height):
        r = rgb_data[i*3] >> 3
        g = rgb_data[i*3 + 1] >> 2
        b = rgb_data[i*3 + 2] >> 3
        pixel = (r << 11) | (g << 5) | b
        struct.pack_into('<H', rgb565_data, i * 2, pixel)

    # Encode en Base64 pour insérer dans un fichier Python
    b64_data = base64.b64encode(rgb565_data).decode('ascii')

    # Contenu du fichier ui_images.py
    python_file_content = f"""# Ce fichier est généré automatiquement
import base64

width = {width}
height = {height}
rgb565_b64 = \"\"\"{b64_data}\"\"\"

def get_image_bytes():
    return base64.b64decode(rgb565_b64)
"""

    return Response(
        python_file_content,
        mimetype='text/plain',
        headers={"Content-Disposition": "attachment; filename=ui_images.py"}
    )

if __name__ == '__main__':
    app.run()
