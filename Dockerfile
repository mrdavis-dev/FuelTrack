#FROM python:3.9
FROM python:alpine

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de la aplicación al contenedor
COPY . /app

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que la aplicación se ejecutará
EXPOSE 5000

# Establece la variable de entorno FLASK_APP con el nombre del archivo principal de la aplicación Flask
ENV FLASK_APP=app.py

# Establece la variable de entorno FLASK_ENV para habilitar el modo de depuración
ENV FLASK_ENV=development

# Ejecuta el comando para iniciar la aplicación Flask
CMD ["flask", "run", "--host=0.0.0.0"]
