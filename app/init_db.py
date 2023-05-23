import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)

    if conn:
        return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def main():
    database = r"./roles.db"

    sql_create_admin_table = """ CREATE TABLE IF NOT EXISTS admin (
                                    username text PRIMARY KEY,
                                    password text NOT NULL
                                ); """

    sql_create_company_table = """CREATE TABLE IF NOT EXISTS company (
                                    id integer PRIMARY KEY,
                                    company_name text NOT NULL,
                                    company_api_key text NOT NULL
                                );"""

    sql_create_location_table = """CREATE TABLE IF NOT EXISTS location (
                                    company_id integer NOT NULL,
                                    location_name text NOT NULL,
                                    location_country text NOT NULL,
                                    location_city text NOT NULL,
                                    location_meta text,
                                    FOREIGN KEY (company_id) REFERENCES company (id)
                                );"""

    sql_create_sensor_table = """CREATE TABLE IF NOT EXISTS sensor (
                                    location_id integer NOT NULL,
                                    sensor_id integer PRIMARY KEY,
                                    sensor_name text NOT NULL,
                                    sensor_category text NOT NULL,
                                    sensor_meta text,
                                    sensor_api_key text NOT NULL,
                                    FOREIGN KEY (location_id) REFERENCES location (company_id)
                                );"""

    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_admin_table)
        create_table(conn, sql_create_company_table)
        create_table(conn, sql_create_location_table)
        create_table(conn, sql_create_sensor_table)
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
