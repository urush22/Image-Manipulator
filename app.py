from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from PIL import Image
import pandas as pd
import requests
import urllib.request

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.expanduser("~/Downloads")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def download_images_via_url(img_url, file_path, width=None, height=None):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
        }
        req = urllib.request.Request(img_url, headers=headers)
        with urllib.request.urlopen(req) as response:
            with open(file_path, 'wb') as out_file:
                out_file.write(response.read())

        if width is not None and height is not None:
            with Image.open(file_path) as img:
                resized_img = img.resize((width, height))
                resized_img.save(file_path, format=img.format)
        return True, "Image downloaded successfully"
    except Exception as e:
        return False, str(e)

def process_csv_file(csv_file, save_dir, width=None, height=None):
    try:
        df = pd.read_csv(csv_file)
        results = []
        for index, row in df.iterrows():
            image_url = row['image_url']
            image_name = f"{row['image_name']}.jpg" if 'image_name' in df.columns else f"{index}.jpg"
            file_path = os.path.join(save_dir, image_name)

            try:
                response = requests.get(image_url, stream=True)
                response.raise_for_status()

                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)

                if width is not None and height is not None:
                    with Image.open(file_path) as img:
                        resized_img = img.resize((width, height))
                        resized_img.save(file_path)
                results.append({"status": "success", "file": image_name})
            except Exception as e:
                results.append({"status": "error", "file": image_name, "error": str(e)})
        return True, results
    except Exception as e:
        return False, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download_single', methods=['POST'])
def download_single():
    img_url = request.form.get('imageUrl')
    file_name = request.form.get('fileName')
    width = request.form.get('width', type=int)
    height = request.form.get('height', type=int)

    if not img_url or not file_name:
        return jsonify({"success": False, "message": "Please provide both image URL and file name"})

    save_dir = app.config['UPLOAD_FOLDER']
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, secure_filename(file_name))

    success, message = download_images_via_url(
        img_url,
        file_path,
        width if width and width > 0 else None,
        height if height and height > 0 else None
    )

    return jsonify({"success": success, "message": message})

@app.route('/download_bulk', methods=['POST'])
def download_bulk():
    if 'csvFile' not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"})

    csv_file = request.files['csvFile']
    width = request.form.get('widthCsv', type=int)
    height = request.form.get('heightCsv', type=int)

    if csv_file.filename == '':
        return jsonify({"success": False, "message": "No file selected"})

    save_dir = app.config['UPLOAD_FOLDER']
    os.makedirs(save_dir, exist_ok=True)

    success, results = process_csv_file(
        csv_file,
        save_dir,
        width if width and width > 0 else None,
        height if height and height > 0 else None
    )

    return jsonify({
        "success": success,
        "results": results if success else None,
        "message": results if not success else None
    })

if __name__ == '__main__':
    app.run(debug=True)