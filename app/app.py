from flask import Flask, request, jsonify, abort
import sqlite3

app = Flask(__name__)

@app.route('/', methods=['POST'])
def get_tables():
    if not request.json:
        abort(400)

    # los datos enviados en el cuerpo del mensaje POST están disponibles en request.json
    data = request.json

    # y finalmente, puedes devolver una respuesta
    return jsonify({'resultado': data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
