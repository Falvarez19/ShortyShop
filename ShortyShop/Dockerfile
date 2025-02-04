# Usa la imagen oficial de Python
FROM python:3.12

# Establecer el directorio de trabajo en el contenedor
WORKDIR /code

# Copiar los archivos del proyecto
COPY . /code/

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 8000
EXPOSE 8000

# Comando para ejecutar Django en producción
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ShortyShop.wsgi:application"]
