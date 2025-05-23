from flask import Flask, request, render_template, send_from_directory, send_file
from rembg import remove
from PIL import Image
import os
import zipfile
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/process', methods=['POST'])
def process():
    files = request.files.getlist('images')
    if not files:
        return "No files uploaded", 400

    processed_files = []

    for file in files:
        img = Image.open(file).convert("RGBA")
        result = remove(img)

        filename = file.filename.rsplit('.', 1)[0] + "_no_bg.png"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        result.save(save_path)

        processed_files.append({
            "original": file.filename,
            "result": filename
        })

    return render_template("result.html", files=processed_files)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/download_all')
def download_all():
    # List semua file di folder uploads yang ingin di zip
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    png_files = [f for f in files if f.endswith('_no_bg.png')]

    # Jika tidak ada file, kembalikan error
    if not png_files:
        return "No files to download", 404

    # Buat ZIP di memory
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for filename in png_files:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            zf.write(filepath, arcname=filename)
    memory_file.seek(0)

    return send_file(
        memory_file,
        mimetype='application/zip',
        download_name='all_no_bg_images.zip',
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True)
