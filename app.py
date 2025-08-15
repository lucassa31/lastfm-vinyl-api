from flask import Flask, request, Response
from PIL import Image
import requests
import io
import struct

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

    # Conversion manuelle de RGB en RGB565
    width, height = img.size
    rgb_data = img.tobytes()
    rgb565_data = bytearray(width * height * 2)

    for i in range(width * height):
        r = rgb_data[i*3] >> 3
        g = rgb_data[i*3 + 1] >> 2
        b = rgb_data[i*3 + 2] >> 3
        pixel = (r << 11) | (g << 5) | b
        struct.pack_into('<H', rgb565_data, i * 2, pixel)

    output_stream = io.BytesIO(rgb565_data)
    output_stream.seek(0)

    return Response(output_stream, mimetype='application/octet-stream')

if __name__ == '__main__':
    app.run()
