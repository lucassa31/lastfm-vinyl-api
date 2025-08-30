from flask import Flask, request, Response
from PIL import Image
import requests
import io
import struct

app = Flask(__name__)

@app.route('/convert_and_generate', methods=['GET'])
def convert_and_generate():
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
        
        # Le format LVGL par défaut est Little-Endian
        rgb565 = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
        lv_bytes.extend(struct.pack('<H', rgb565))

    # Retourne les données binaires brutes directement
    return Response(
        lv_bytes,
        mimetype="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=album_art.bin"}
    )

if __name__ == '__main__':
    app.run()
