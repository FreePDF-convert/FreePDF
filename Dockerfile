# Imagen base con Ubuntu
FROM ubuntu:22.04

# Evita las preguntas interactivas al instalar
ENV DEBIAN_FRONTEND=noninteractive

# Actualiza e instala Python, LibreOffice y dependencias
RUN apt-get update && apt-get install -y \
    libreoffice \
    python3 \
    python3-pip \
    python3-dev \
    unzip \
    fonts-dejavu \
    fonts-liberation \
    && apt-get clean

# Instala paquetes de Python
RUN pip3 install flask PyPDF2 pillow docx2txt pdf2docx

# Crea carpeta de trabajo
WORKDIR /app

# Copia todo el contenido del proyecto a la imagen
COPY . /app

# Expone el puerto
EXPOSE 5000

# Comando que ejecuta Flask
CMD ["python3", "app.py"]
