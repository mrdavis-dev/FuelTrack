import math
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
db = mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return render_template('index.html')

# Ruta para la página de datos_consumo
@app.route('/datos_consumo', methods=['GET'])
def datos_consumo():
    return render_template('datos_consumo.html')

# Ruta para consultar los datos de consumo
@app.route('/consultar', methods=['POST'])
def consultar():
    print("Se ejecutó la función consultar()")
    placa = request.form.get('placa')
    tipo_combustible = request.form.get('tipo_combustible')
    intervalo = request.form.get('intervalo')
    fecha = request.form.get('fecha')

    # Realizar la consulta SQL en la base de datos para obtener los resultados
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        
        if intervalo == 'dia':
                query = "SELECT placa, tipo_combustible, DATE(fecha) AS intervalo, SUM(litros) AS litros_utilizados, SUM(total_venta) AS costo_total FROM consumo WHERE placa = %s AND tipo_combustible = %s AND DATE(fecha) = %s GROUP BY placa, tipo_combustible, DATE(fecha)"
                cursor.execute(query, (placa, tipo_combustible, fecha))
        elif intervalo == 'semana':
                query = "SELECT placa, tipo_combustible, WEEK(fecha) AS intervalo, SUM(litros) AS litros_utilizados, SUM(total_venta) AS costo_total FROM consumo WHERE placa = %s AND tipo_combustible = %s AND WEEK(fecha) = WEEK(CURDATE()) GROUP BY placa, tipo_combustible, WEEK(fecha)"
                cursor.execute(query, (placa, tipo_combustible))
        elif intervalo == 'mes':
                query = "SELECT placa, tipo_combustible, MONTH(fecha) AS intervalo, SUM(litros) AS litros_utilizados, SUM(total_venta) AS costo_total FROM consumo WHERE placa = %s AND tipo_combustible = %s AND MONTH(fecha) = MONTH(CURDATE()) GROUP BY placa, tipo_combustible, MONTH(fecha)"
                cursor.execute(query, (placa, tipo_combustible))
        
        resultados = cursor.fetchall()
    except mysql.connector.Error as error:
        print("Error al consultar la base de datos: {}".format(error))
        resultados = []
        print("Resultados:", resultados)
    # Renderizar la plantilla con los resultados de la consulta
    return render_template('datos_consumo.html', resultados=resultados)


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
    

# Ruta para la página "informe"
@app.route('/informe', methods=['GET'])
def informe():
    fecha = request.args.get('fecha')
    
    # Realizar la consulta SQL para obtener los registros de consumo por fecha
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM consumo WHERE fecha = %s"
        cursor.execute(query, (fecha,))
        registros_consumo = cursor.fetchall()
    except mysql.connector.Error as error:
        print("Error al consultar la base de datos: {}".format(error))
        registros_consumo = []

    # Renderizar la plantilla con los registros de consumo
    return render_template('informe.html', registros_consumo=registros_consumo)




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