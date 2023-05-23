# Usar la imagen oficial de Python en Alpine como base
FROM python:3.11-alpine

# Copiar el contenido del directorio local a /app en el contenedor
COPY . .

# Añadir el compilador y las librerías necesarias para instalar paquetes
RUN apk update && apk add --no-cache --virtual .build-deps gcc musl-dev sqlite

# Instalar las dependencias de Python
RUN pip install flask

# Desinstalar el compilador y las librerías no necesarias
RUN apk del .build-deps

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Iniciar el servidor Flask
CMD ["sh", "init.sh"]
