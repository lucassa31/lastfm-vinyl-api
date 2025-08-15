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

    try:
        # Assurez-vous d'abord que le mode est RGB
        img = img.convert("RGB")

        # Convertissez l'image au format RGB565
        # Les données de l'image sont maintenant au bon format
        data_rgb565 = img.tobytes()

        # Recréez une image Pillow au format RGB565
        img_final = Image.frombytes("RGB565", img.size, data_rgb565)

        # Redimensionnez l'image finale
        img_final = img_final.resize((240, 240))

    except Exception as e:
        return f"Erreur de conversion: {e}", 500

    output_stream = io.BytesIO(img_final.tobytes())
    output_stream.seek(0)

    return Response(output_stream, mimetype='application/octet-stream')

if __name__ == '__main__':
    app.run()
