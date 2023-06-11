import sqlite3

def login_admin(credential_cookie:str, db_name:str) -> bool:
    try:
        username, password = credential_cookie.split("<sep>")
        if username and password:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()

            cursor.execute(f"SELECT COUNT(*) FROM Admin WHERE Username='{username}' AND Password='{password}';")
            result = cursor.fetchall()

            conn.close()
            if result[0][0] == 1:
                return True
            else:
                return False
    except:
        return False
    
def verify_company_api_key(company_api_key:str, db_name:str) -> bool:
    try:
        db = sqlite3.connect(db_name)
        cursor = db.cursor()

        cursor.execute(f"SELECT COUNT(*) FROM Company WHERE company_api_key='{company_api_key}';")
        result = cursor.fetchone()

        db.close()

        if result[0] == 0:
            return False
        else:
            return True

    except sqlite3.Error as e:
        print(f"Error: {str(e)}")
        return False
    
def verify_sensor_api_key(api_key, db_name):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        cursor.execute(f"SELECT sensor_id FROM Sensor WHERE sensor_api_key = '{api_key}';")
        result = cursor.fetchall()
        conn.close()

        if result:
            return True, result[0][0]
        else:
            return False, None
    except sqlite3.Error as e:
        return False, None
