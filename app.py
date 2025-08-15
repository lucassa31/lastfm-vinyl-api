from flask import Flask, request, Response
from PIL import Image
import requests
import io

app = Flask(__name__)

@app.route('/convert_and_stream', methods=['GET'])
def convert_and_stream():
    image_url = request.args.get('url')
    if not image_url:
        return "URL d'image manquante", 400

    try:
        response = requests.get(image_url)
        img = Image.open(io.BytesIO(response.content))
    except Exception:
        return "Erreur lors de l'ouverture de l'image", 400

    # Redimensionnement et conversion en une seule ligne
    img = img.resize((240, 240)).convert('RGB').convert('RGB565', dither=Image.NONE)

    output_stream = io.BytesIO(img.tobytes())
    output_stream.seek(0)

    return Response(output_stream, mimetype='application/octet-stream')

if __name__ == '__main__':
    app.run()
