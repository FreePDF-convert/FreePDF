from flask import Flask, render_template, request, send_file
import os
from werkzeug.utils import secure_filename
from fpdf import FPDF
import uuid

app = Flask(__name__)

# Crear carpeta 'uploads' si no existe
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part", 400

        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return "No file selected", 400

        # Verificamos que sea .txt
        if not uploaded_file.filename.lower().endswith('.txt'):
            return "Only .txt files are supported at the moment.", 400

        # Guardar el archivo
        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(file_path)

        # Leer y convertir a PDF
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            return f"Error reading the file: {e}", 500

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in text.split('\n'):
            pdf.multi_cell(0, 10, line)  # Mejor que cell() para líneas largas

        pdf_filename = f"{uuid.uuid4().hex}.pdf"
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        pdf.output(pdf_path)

        return send_file(pdf_path, as_attachment=True)

    return render_template('index.html')
