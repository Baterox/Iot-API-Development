# Use an official Python runtime as a parent image
FROM python:alpine3.18

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir flask python-dotenv

# Install sqlite3 from the alpine repositories
RUN apk add --no-cache sqlite

# Run the SQL script to create the database
RUN sqlite3 iot_bbdd.db < init.sql

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the flask server when the container launches
CMD ["python", "app.py"]