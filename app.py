from flask import Flask, render_template, request, jsonify, redirect
import mysql.connector
from datetime import datetime


app = Flask(__name__)
app.config['DEBUG'] = True

# Configuración de la conexión a la base de datos MySQL
db_config = {
    'host': 'bxlctm1oclck3tw4l6dq-mysql.services.clever-cloud.com',
    'user': 'up2jjdlqwbgka3uk',
    'password': '7HnKH2Eg3ehXs6g6GIsS',
    'database': 'bxlctm1oclck3tw4l6dq',
    'charset': 'utf8mb4'
}

@app.route('/')
def index():
    return render_template('index.html')

# Ruta para buscar el vehículo
@app.route('/buscar_placa', methods=['POST'])
def buscar_placa():
    placa = request.form['placa']

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    query = "SELECT * FROM vehiculos WHERE placa = %s"
    cursor.execute(query, (placa,))
    vehiculo = cursor.fetchone()

    cursor.close()
    conn.close()


    if vehiculo:
        # Renderizar una plantilla de resultado con los datos del vehículo
        return render_template('resultado_vehiculo.html', vehiculo=vehiculo)
    else:
        # Enviar una respuesta JSON si no se encuentra el vehículo
        return jsonify({'error': 'Vehículo no encontrado'})
    

@app.route('/guardar_registro', methods=['POST'])
def guardar_registro():
    placa = request.form['placa']
    conductor = request.form['conductor']
    odometro = int(request.form['odometro'])
    departamento = request.form['departamento']
    litros = float(request.form['litros'])
    tipo_combustible = request.form['tipo_combustible']
    descripcion = request.form['descripcion']
    factura = request.form['factura']
    precio_gas = float(request.form['precio_gas'])
    total_venta = float(request.form['total_venta'])
    fecha = datetime.now()

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    query = "INSERT INTO consumo (placa, conductor, odometro, departamento, litros, tipo_combustible, descripcion, factura, precio_gas, total_venta, fecha) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (placa, conductor, odometro, departamento, litros, tipo_combustible, descripcion, factura, precio_gas, total_venta, fecha)
    cursor.execute(query, values)

    conn.commit()

    cursor.close()
    conn.close()

    return redirect('/')

if __name__ == '__main__':
    app.run()