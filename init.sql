-- ADMIN TABLE
CREATE TABLE Admin (
    Username TEXT PRIMARY KEY,
    Password TEXT NOT NULL
);

-- COMPANY TABLE
CREATE TABLE Company (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    company_api_key TEXT NOT NULL UNIQUE
);

-- LOCATION TABLE
CREATE TABLE Location (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    location_name TEXT,
    location_country TEXT,
    location_city TEXT,
    location_meta TEXT,
    FOREIGN KEY (company_id) REFERENCES Company(company_id)
);

-- SENSOR TABLE
CREATE TABLE Sensor (
    sensor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER,
    sensor_name TEXT,
    sensor_category TEXT,
    sensor_meta TEXT,
    sensor_api_key TEXT NOT NULL UNIQUE,
    FOREIGN KEY (location_id) REFERENCES Location(id)
);

-- SENSOR DATA TABLE
CREATE TABLE "Sensor Data" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER,
    epoch INTEGER,
    parametro TEXT,
    captura REAL,
    FOREIGN KEY (sensor_id) REFERENCES Sensor(sensor_id)
);

-- CREA USUARIO ADMIN
INSERT INTO Admin (Username, Password)
VALUES ('admin', 'admin0582.,');