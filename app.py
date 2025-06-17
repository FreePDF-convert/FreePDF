from flask import Flask, render_template, request, send_file, redirect
import os
from werkzeug.utils import secure_filename
import uuid
from PyPDF2 import PdfMerger
from PIL import Image
import docx2txt
from pdf2docx import Converter

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crear carpetas si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return "No file selected", 400

        filename = secure_filename(uploaded_file.filename)
        ext = filename.split('.')[-1].lower()
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(file_path)

        pdf_filename = f"{uuid.uuid4().hex}.pdf"
        pdf_path = os.path.join(OUTPUT_FOLDER, pdf_filename)

        try:
            if ext == 'txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

                from fpdf import FPDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for line in text.split('\n'):
                    pdf.cell(200, 10, txt=line, ln=1)
                pdf.output(pdf_path)

            elif ext in ['jpg', 'jpeg', 'png']:
                image = Image.open(file_path).convert('RGB')
                image.save(pdf_path)

            elif ext == 'docx':
                text = docx2txt.process(file_path)
                from fpdf import FPDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for line in text.split('\n'):
                    pdf.multi_cell(0, 10, txt=line)
                pdf.output(pdf_path)

            elif ext == 'pdf':
                # Ya es PDF, simplemente devuélvelo
                return send_file(file_path, as_attachment=True)

            else:
                return "Unsupported file type", 400

            return send_file(pdf_path, as_attachment=True)

        except Exception as e:
            return f"Error al convertir el archivo: {str(e)}", 500

    return render_template('index.html')
    
@app.route('/pdf-to-docx', methods=['POST'])
def pdf_to_docx():
    file = request.files['file']
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)

        output_filename = filename.replace('.pdf', '.docx')
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        cv = Converter(input_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()

        return send_file(output_path, as_attachment=True)

    return redirect('/')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
