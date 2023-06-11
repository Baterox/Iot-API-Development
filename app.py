from flask import Flask, request, jsonify
import sqlite3
import os
from dotenv import load_dotenv
from modules.validation import login_admin, verify_company_api_key, verify_sensor_api_key
import secrets
import time

load_dotenv()
db_name = os.getenv("DB_NAME")
app = Flask(__name__)

# CREAR COMPAÑÍA -> INICIO DE SESIÓN DE ADMINISTRADOR NECESARIO
@app.route("/api/v1/admin/create_company", methods=['POST'])
def create_company():
    if request.method == 'POST':
        try:
            # RECIBIMOS LOS DATOS ENVIADOS
            data = request.get_json()
            company_name = data['company_name']
            credential = request.headers["credential"]
            company_api_key = secrets.token_urlsafe(16)
            
            # VERFICAMOS INICIO DE SESIÓN
            if not login_admin(credential, db_name):
                return jsonify({"mensaje": f"No se pudo crear la compañía"}), 401
            
            db = sqlite3.connect(db_name)
            cursor = db.cursor()

            cursor.execute(f"INSERT INTO Company (company_name, company_api_key) VALUES ('{company_name}', '{company_api_key}');")

            db.commit()
            db.close()

            return jsonify({"mensaje": "Compañia creada exitosamente", "company_api_key": company_api_key}), 200
        
        except:
            return jsonify({"mensaje": f"No se pudo crear la compañía"}), 500

# CREAR LOCALIZACIÓN -> INICIO DE SESIÓN DE ADMINISTRADOR NECESARIO
@app.route("/api/v1/admin/create_location", methods=['POST'])
def create_location():
    if request.method == 'POST':
        try:
            # RECIBIMOS LOS DATOS ENVIADOS
            data = request.get_json()
            company_name = data['company_id']
            location_name = data['location_name']
            location_country = data['location_country']
            location_city = data['location_city']
            location_meta = data['location_meta']
            credential = request.headers["credential"]

            # VERFICAMOS INICIO DE SESIÓN
            if not login_admin(credential, db_name):
                return jsonify({"mensaje": f"No se pudo crear la localización"}), 401

            db = sqlite3.connect(db_name)
            cursor = db.cursor()

            cursor.execute(f"""INSERT INTO Location (company_id, location_name, location_country, location_city, location_meta) 
                                VALUES ('{company_name}', '{location_name}', '{location_country}', '{location_city}', '{location_meta}');""")
            db.commit()
            db.close()

            return jsonify({"mensaje": "Ubicación creada exitosamente"}), 200
        except:
            return jsonify({"mensaje": f"No se pudo crear la localización: {str(e)}"}), 500

# CREAR SENSOR -> INICIO DE SESIÓN DE ADMINISTRADOR NECESARIO
@app.route("/api/v1/admin/create_sensor", methods=['POST'])
def createSensor():
    if request.method == 'POST':
        try:
            data = request.get_json()
            location_id = data['location_id']
            sensor_name = data['sensor_name']
            sensor_category = data['sensor_category']
            sensor_meta = data['sensor_meta']
            credential = request.headers["credential"]
            sensor_api_key = secrets.token_urlsafe(16)

            # VERFICAMOS INICIO DE SESIÓN
            if not login_admin(credential, db_name):
                return jsonify({"mensaje": f"No se pudo crear el sensor"}), 401

            db = sqlite3.connect(db_name)
            cursor = db.cursor()

            cursor.execute(f"""INSERT INTO Sensor (location_id, sensor_name, sensor_category, sensor_meta, sensor_api_key) 
                                VALUES ('{location_id}', '{sensor_name}', '{sensor_category}', '{sensor_meta}', '{sensor_api_key}');""")

            db.commit()
            db.close()

            return jsonify({"mensaje": "Sensor creado exitosamente", "sensor_api_key": sensor_api_key}), 200
        
        except:
            return jsonify({"mensaje": f"No se pudo crear el sensor"}), 500

# SHOW ALL BY TABLE -> AUTENTIFICACIÓN CON COMPANY API KEY
@app.route("/api/v1/show_all/<string:table_name>&<string:company_api_key>", methods=['GET'])
def get_table(table_name, company_api_key):
    if table_name.lower() in ['admin', 'company']:
        return jsonify({"mensaje": f"Error, acceso a la tabla {table_name} denegado"}), 403

    try:
        if verify_company_api_key(company_api_key, db_name):
            db = sqlite3.connect(db_name)
            cursor = db.cursor()

            cursor.execute(f"SELECT * FROM {table_name};")
            records = cursor.fetchall()

            db.close()

            return jsonify({table_name: records}), 200
        else:
            return jsonify({"mensaje": "Error, company api key incorrecto"}), 400

    except sqlite3.Error as e:
        return jsonify({"mensaje": f"Error al mostrar la tabla {table_name}: {str(e)}"}), 500

# SHOW ONE BY TABLE -> AUTENTIFICACIÓN CON COMPANY API KEY
@app.route("/api/v1/show_one/<string:table_name>&<string:id>&<string:company_api_key>", methods=['GET'])
def get_row_one(table_name, id, company_api_key):
    if table_name.lower() in ['admin', 'company']:
        return jsonify({"mensaje": f"Error, acceso a la tabla {table_name} denegado"}), 403

    if not verify_company_api_key(company_api_key, db_name):
        return jsonify({"mensaje": "Error, company api key incorrecto"}), 400

    try:
        db = sqlite3.connect(db_name)
        cursor = db.cursor()

        id_column = "sensor_id" if table_name.lower() == "sensor" else "id"

        cursor.execute(f"SELECT * FROM {table_name} WHERE {id_column}='{id}';")
        record = cursor.fetchone()

        db.close()

        if record is None:
            return jsonify({"mensaje": f"No se encontró la entrada con id {id} en la tabla {table_name}"}), 404

        return jsonify({table_name: record}), 200
    except sqlite3.Error as e:
        return jsonify({"mensaje": f"Error al mostrar la tabla {table_name}: {str(e)}"}), 500

# UPDATE LOCATION BY ID -> AUTENTIFICACIÓN CON COMPANY API KEY
@app.route("/api/v1/company/update_location/<int:id>&<string:company_api_key>", methods=['PUT'])
def edit_location(id, company_api_key):
    if request.method == 'PUT':
        data = request.get_json()
        company_id = data['company_id']
        location_name = data['location_name']
        location_country = data['location_country']
        location_city = data['location_city']
        location_meta = data['location_meta']
        id = id

        # VERIFICAMOS EL COMPANY API KEY
        if not verify_company_api_key(company_api_key, db_name):
            return jsonify({"mensaje": "No se pudo actualizar la localización."}), 401

        try:
            db = sqlite3.connect(db_name)
            cursor = db.cursor()
            cursor.execute(f"""UPDATE Location SET company_id = '{company_id}', location_name = '{location_name}', 
                            location_country = '{location_country}', location_city = '{location_city}', 
                            location_meta = '{location_meta}' WHERE id = {id}""")
            db.commit()
            db.close()

            return jsonify({"mensaje": "Localización actualizada exitosamente."}), 200
        except:
            return jsonify({"mensaje": f"No se pudo actualizar la localización."}), 500

# UPDATE SENSOR BY ID -> AUTENTIFICACIÓN CON COMPANY API KEY
@app.route("/api/v1/company/update_sensor/<int:id>&<string:company_api_key>", methods=['PUT'])
def edit_sensor(id, company_api_key):
    if request.method == 'PUT':
        try:
            data = request.get_json()
            location_id = data['location_id']
            sensor_name = data['sensor_name']
            sensor_category = data['sensor_category']
            sensor_meta = data['sensor_meta']
            sensor_api_key = data['sensor_api_key']
            id = id

            # VERIFICAMOS EL COMPANY API KEY
            if not verify_company_api_key(company_api_key, db_name):
                return jsonify({"mensaje": "No se pudo actualizar el sensor."}), 401
        
            db = sqlite3.connect(db_name)
            cursor = db.cursor()
            cursor.execute(f"""UPDATE Sensor SET location_id = '{location_id}', sensor_name = '{sensor_name}', 
                            sensor_category = '{sensor_category}', sensor_meta = '{sensor_meta}', 
                            sensor_api_key = '{sensor_api_key}' WHERE sensor_id = '{id}'""")
            db.commit()
            db.close()

            return jsonify({"mensaje": "Sensor actualizado exitosamente."}), 200
        except:
            return jsonify({"mensaje": f"No se pudo actualizar el sensor."}), 500

# UPDATE SENSOR DATA BY ID -> AUTENTIFICACIÓN CON COMPANY API KEY
@app.route("/api/v1/company/update_sensor_data/<int:id>&<string:company_api_key>", methods=['PUT'])
def edit_sensor_data(id, company_api_key):
    if request.method == 'PUT':
        try:
            data = request.get_json()
            sensor_id = data['sensor_id']
            epoch = data['epoch']
            parametro = data['parametro']
            captura = data['captura']
            id = id

            # VERIFICAMOS EL COMPANY API KEY
            if not verify_company_api_key(company_api_key, db_name):
                return jsonify({"mensaje": "No se pudo actualizar la data capturada por el sensor."}), 401

            db = sqlite3.connect(db_name)
            cursor = db.cursor()
            cursor.execute(f"""UPDATE "Sensor Data" SET sensor_id = '{sensor_id}', epoch = '{epoch}', parametro = '{parametro}', captura = '{captura}'
                            WHERE id = {id}""")
            db.commit()
            db.close()

            return jsonify({"mensaje": "Datos del sensor data actualizados exitosamente"}), 200
        except:
            return jsonify({"mensaje": f"No se pudo actualizar la data capturada por el sensor."}), 500

# DELETE LOCATION BY ID -> AUTENTIFICACIÓN CON COMPANY API KEY
@app.route("/api/v1/company/delete_location/<int:id>&<string:company_api_key>", methods=['DELETE'])
def delete_location(id, company_api_key):
    if request.method == 'DELETE':
        try:
            if not verify_company_api_key(company_api_key, db_name):
                return jsonify({"mensaje": "No se pudo borrar la localización"}), 400
        
            db = sqlite3.connect(db_name)
            cursor = db.cursor()
            cursor.execute(f"""DELETE FROM Location WHERE id = {id}""")
            db.commit()
            db.close()

            return jsonify({"mensaje": "Localización borrada exitosamente"}), 200
        except:
            return jsonify({"mensaje": f"No se pudo borrar la localización"}), 500
 
# DELETE SENSOR BY ID -> AUTENTIFICACIÓN CON COMPANY API KEY
@app.route("/api/v1/company/delete_sensor/<string:sensor_id>&<string:company_api_key>", methods=['DELETE'])
def delete_sensor(sensor_id, company_api_key):
    if request.method == 'DELETE':
        try:
            if not verify_company_api_key(company_api_key, db_name):
                return jsonify({"mensaje": "No se pudo borrar el sensor"}), 400

            db = sqlite3.connect(db_name)
            cursor = db.cursor()
            cursor.execute(f"""DELETE FROM Sensor WHERE sensor_id = '{sensor_id}'""")
            db.commit()
            db.close()

            return jsonify({"mensaje": "Sensor borrado exitosamente"}), 200
        except:
            return jsonify({"mensaje": f"No se pudo borrar el sensor"}), 500

# DELETE SENSOR DATA BY ID -> AUTENTIFICACIÓN CON COMPANY API KEY
@app.route("/api/v1/company/delete_sensor_data/<int:id>&<string:company_api_key>", methods=['DELETE'])
def delete_sensor_data(id, company_api_key):
    if request.method == 'DELETE':
        try:
            if not verify_company_api_key(company_api_key, db_name):
                return jsonify({"mensaje": "No se pudo borrar el sensor data"}), 400

            db = sqlite3.connect(db_name)
            cursor = db.cursor()
            cursor.execute(f"""DELETE FROM "Sensor Data" WHERE id = {id}""")
            db.commit()
            db.close()

            return jsonify({"mensaje": "Datos del sensor eliminados exitosamente"}), 200
        except:
            return jsonify({"mensaje": f"No se pudo borrar el sensor data"}), 500

# SENSOR
@app.route("/api/v1/sensor_data", methods=['POST'])
def insert_sensor_data():
    if request.method == 'POST':
        try:
            data = request.get_json()
            sensor_api_key = data['sensor_api_key']
            json_data = data['json_data']
            epoch = int(time.time())
            
            key_exists, sensor_id = verify_sensor_api_key(sensor_api_key, db_name)
            if not key_exists:
                return jsonify({"mensaje": f"Error al leer datos del sensor"}), 400
        
            db = sqlite3.connect(db_name)
            cursor = db.cursor()

            for record in json_data:
                for parametro, captura in record.items():
                    cursor.execute(f"""INSERT INTO "Sensor Data" (sensor_id, epoch, parametro, captura) 
                                        VALUES ('{sensor_id}', {epoch}, '{parametro}', '{captura}');""")

            db.commit()
            db.close()

            return jsonify({"mensaje": "Datos del sensor insertados exitosamente"}), 200
        except:
            return jsonify({"mensaje": f"Error al leer datos del sensor"}), 500

@app.route("/api/v1/sensor_data/<int:start>&<int:end>&<string:company_api_key>", methods=['GET'])
def get_sensor_data(start, end, company_api_key):
    data = request.get_json()
    sensor_ids = data['sensor_id']

    # If the company_api_key is not valid, return an error message
    if not verify_company_api_key(company_api_key, db_name):
        return jsonify({"mensaje": "Error, company api key incorrecto"}), 400

    # Parse the sensor_ids parameter into a list
    sensor_ids = sensor_ids.strip('][').split(',')

    try:
        db = sqlite3.connect(db_name)
        cursor = db.cursor()

        # Initialize an empty list to store the records
        records = []

        # Get the records for each sensor_id in the given time range
        for sensor_id in sensor_ids:
            cursor.execute(f"""SELECT * FROM "Sensor Data" WHERE sensor_id = '{sensor_id}' 
                            AND epoch BETWEEN {start} AND {end};""")
            records.extend(cursor.fetchall())

        db.close()

        return jsonify({"Sensor Data": records}), 200
    except sqlite3.Error as e:
        return jsonify({"mensaje": f"Error al obtener los datos del sensor: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
