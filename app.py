from flask import Flask, render_template, request, send_file, redirect
import os
from werkzeug.utils import secure_filename
import uuid
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import docx2txt
from pdf2docx import Converter
from fpdf import FPDF

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

        original_filename = secure_filename(uploaded_file.filename)
        ext = original_filename.split('.')[-1].lower()
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
        uploaded_file.save(file_path)

        pdf_filename = original_filename.rsplit('.', 1)[0] + ".pdf"
        pdf_path = os.path.join(OUTPUT_FOLDER, pdf_filename)

        try:
            if ext == 'txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for line in text.split('\n'):
                    pdf.multi_cell(0, 10, txt=line)
                pdf.output(pdf_path)

            elif ext in ['jpg', 'jpeg', 'png']:
                image = Image.open(file_path).convert('RGB')
                image.save(pdf_path)

            elif ext == 'docx':
                filename = os.path.basename(file_path)
                output_doc = os.path.join(OUTPUT_FOLDER, filename.replace('.docx', '.pdf'))
                command = f'libreoffice --headless --convert-to pdf "{file_path}" --outdir"{OUTPUT_FOLDER}"'
                conversion_result = os.system(command)
                if conversion_result !=0 or not os.path.exists(output_doc):
                    return "Error en la conversión con LibreOffice", 500                
                pdf_path = output_doc

            elif ext == 'pdf':
                reader = PdfReader(file_path)
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                with open(pdf_path, 'wb') as f:
                    writer.write(f)
                return send_file(pdf_path, as_attachment=True, download_name=original_filename)

            else:
                return "Unsupported file type", 400

            return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)

        except Exception as e:
            return f"Error al convertir el archivo: {str(e)}", 500

    return render_template('index.html')

@app.route('/pdf-to-docx', methods=['POST'])
def pdf_to_docx():
    file = request.files['file']
    if file and file.filename.endswith('.pdf'):
        original_filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
        file.save(input_path)

        output_filename = original_filename.replace('.pdf', '.docx')
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        cv = Converter(input_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()

        return send_file(output_path, as_attachment=True, download_name=output_filename)

    return redirect('/')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
