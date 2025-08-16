from PIL import Image
import struct

# Nom du fichier à générer
output_file = "ui_images.py"

# Liste de tes images à convertir
images_to_convert = {
    "my_image": "chemin/vers/ton_image.jpg",
    # ajoute d'autres images si besoin :
    # "autre_image": "chemin/vers/autre_image.jpg"
}

with open(output_file, "w") as f:
    f.write("# Ce fichier est généré automatiquement\n\n")
    f.write("import lvgl as lv\n\n")

    for var_name, img_path in images_to_convert.items():
        # Ouvrir et convertir l'image en RGB565
        img = Image.open(img_path).convert("RGB")
        width, height = img.size
        rgb_data = img.tobytes()
        rgb565_data = bytearray(width * height * 2)

        for i in range(width * height):
            r = rgb_data[i*3] >> 3
            g = rgb_data[i*3 + 1] >> 2
            b = rgb_data[i*3 + 2] >> 3
            pixel = (r << 11) | (g << 5) | b
            struct.pack_into('<H', rgb565_data, i * 2, pixel)

        # Écrire l'image dans le fichier Python
        f.write(f"{var_name}_width = {width}\n")
        f.write(f"{var_name}_height = {height}\n")
        f.write(f"{var_name}_data = bytes([\n")
        for i in range(0, len(rgb565_data), 16):
            chunk = ", ".join(str(b) for b in rgb565_data[i:i+16])
            f.write(f"    {chunk},\n")
        f.write("])\n\n")

        f.write(f"{var_name} = lv.img_dsc_t({{\n")
        f.write(f"    'header': {{'width': {var_name}_width, 'height': {var_name}_height, 'cf': lv.COLOR_FORMAT.RGB565}},\n")
        f.write(f"    'data_size': len({var_name}_data),\n")
        f.write(f"    'data': {var_name}_data\n")
        f.write("})\n\n")

print(f"Fichier '{output_file}' généré avec succès !")
