import math
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps

import mysql.connector
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'Fu3ltr4ck2023'

# Configuración de la conexión a la base de datos MySQL
db_config = {
    'host': 'bxlctm1oclck3tw4l6dq-mysql.services.clever-cloud.com',
    'user': 'up2jjdlqwbgka3uk',
    'password': '7HnKH2Eg3ehXs6g6GIsS',
    'database': 'bxlctm1oclck3tw4l6dq',
    'charset': 'utf8mb4'
}
db = mysql.connector.connect(**db_config)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            db = mysql.connector.connect(**db_config)
            cursor = db.cursor(dictionary=True)

            # Obtener los datos del usuario desde la base de datos
            cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user['contraseña'], password):
                # Almacenar el usuario en la sesión
                session['user'] = user

                tipouser = user['tipo_usuario']
                session['tipo_usuario'] = tipouser

                return redirect(url_for('index'))
            else:
                return render_template('login.html', error='Credenciales incorrectas')
        except mysql.connector.Error as error:
            print("Error al conectar a la base de datos: {}".format(error))
            return render_template('error.html')
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
#fin de login

@app.context_processor
def inject_tipo_usuario():
    # Obtener el tipo de usuario desde la sesión
    tipo_usuario = session.get('tipo_usuario')

    # Retornar un diccionario con la variable que quieres pasar a todas las plantillas
    return {'tipo_usuario': tipo_usuario}


@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Ruta para la página de datos_consumo
@app.route('/datos_consumo', methods=['GET'])
@login_required
def datos_consumo():
    return render_template('datos_consumo.html')

#ruta para vehículos
@app.route('/vehiculos')
@login_required
def vehiculos():
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        
        # Obtener la lista de vehículos desde la base de datos
        cursor.execute("SELECT * FROM vehiculos")
        vehiculos = cursor.fetchall()
        
        return render_template('vehiculos.html', vehiculos=vehiculos)
    except mysql.connector.Error as error:
        print("Error al conectar a la base de datos: {}".format(error))
        return render_template('error.html')

# Ruta para agregar un nuevo vehículo
@app.route('/agregar', methods=['GET', 'POST'])
@login_required
def agregar_vehiculo():
    if request.method == 'POST':
        placa = request.form['placa']
        ano = request.form['ano']
        modelo = request.form['modelo']
        marca = request.form['marca']
        tipoV = request.form['tipoV']
        departamento = request.form['departamento']
        taller = request.form['taller']
        descripcion = request.form['descripcion']
        foto = request.files['foto']
        
        try:
            db = mysql.connector.connect(**db_config)
            cursor = db.cursor()
            
            # Insertar el nuevo vehículo en la base de datos
            cursor.execute("INSERT INTO vehiculos (placa, año, modelo, marca, tipoV, departamento, taller, descripcion, foto) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (placa, ano, modelo, marca, tipoV, departamento, taller, descripcion, foto.filename))
            db.commit()
            
            # Guardar la foto en el sistema de archivos
            foto.save("static/fotos/" + foto.filename)
            
            return redirect('/')
        except mysql.connector.Error as error:
            print("Error al conectar a la base de datos: {}".format(error))
            return render_template('error.html')
    else:
        return render_template('agregar_vehiculo.html')

# Ruta para editar un vehículo
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_vehiculo(id):
    if request.method == 'POST':
        placa = request.form['placa']
        ano = request.form['año']
        modelo = request.form['modelo']
        marca = request.form['marca']
        tipoV = request.form['tipoV']
        departamento = request.form['departamento']
        taller = request.form['taller']
        descripcion = request.form['descripcion']
        
        try:
            db = mysql.connector.connect(**db_config)
            cursor = db.cursor()
            
            # Actualizar el vehículo en la base de datos
            cursor.execute("UPDATE vehiculos SET placa=%s, año=%s, modelo=%s, marca=%s, tipoV=%s, departamento=%s, taller=%s, descripcion=%s WHERE id=%s",
                           (placa, ano, modelo, marca, tipoV, departamento, taller, descripcion, id))
            db.commit()
            
            return redirect('/')
        except mysql.connector.Error as error:
            print("Error al conectar a la base de datos: {}".format(error))
            return render_template('error.html')
    else:
        try:
            db = mysql.connector.connect(**db_config)
            cursor = db.cursor(dictionary=True)
            
            # Obtener los datos del vehículo desde la base de datos
            cursor.execute("SELECT * FROM vehiculos WHERE id=%s", (id,))
            vehiculo = cursor.fetchone()
            
            return render_template('editar_vehiculo.html', vehiculo=vehiculo)
        except mysql.connector.Error as error:
            print("Error al conectar a la base de datos: {}".format(error))
            return render_template('error.html')

# Ruta para eliminar un vehículo
@app.route('/eliminar/<int:id>')
@login_required
def eliminar_vehiculo(id):
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()
        
        # Eliminar el vehículo de la base de datos
        cursor.execute("DELETE FROM vehiculos WHERE id=%s", (id,))
        db.commit()
        
        return redirect('/')
    except mysql.connector.Error as error:
        print("Error al conectar a la base de datos: {}".format(error))
        return render_template('error.html')



# Ruta para consultar los datos de consumo
@app.route('/consultar', methods=['POST'])
@login_required
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
@login_required
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
@login_required
def informe():
    fecha = request.args.get('fecha')
    
    # Realizar la consulta SQL para obtener los registros de consumo por fecha
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        if fecha:
            query = "SELECT * FROM consumo WHERE fecha = %s"
            cursor.execute(query, (fecha,))
        else:
            query = "SELECT * FROM consumo"
            cursor.execute(query)
        
        registros_consumo = cursor.fetchall()
    except mysql.connector.Error as error:
        print("Error al consultar la base de datos: {}".format(error))
        registros_consumo = []

    # Renderizar la plantilla con los registros de consumo
    return render_template('informe.html', registros_consumo=registros_consumo)




@app.route('/guardar_registro', methods=['POST'])
@login_required
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
    #total_venta = float(request.form['total_venta'])
    total_venta = float(precio_gas*litros)
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


# CRUD de Usuarios

@app.route('/usuarios')
@login_required
def usuarios():
    # Obtener la lista de usuarios desde la base de datos
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/agregar_usuario', methods=['GET', 'POST'])
@login_required
def agregar_usuario():
    if request.method == 'POST':
        # Obtener los datos del formulario
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']
        nombre = request.form['nombre']
        tipo_usuario = request.form['tipo_usuario']

        # Cifrar la contraseña
        contraseña_cifrada = generate_password_hash(contraseña)

        # Guardar los datos en la base de datos
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()
        query = "INSERT INTO usuarios (usuario, contraseña, nombre, tipo_usuario) VALUES (%s, %s, %s, %s)"
        values = (usuario, contraseña_cifrada, nombre, tipo_usuario)
        cursor.execute(query, values)
        db.commit()

        return redirect(url_for('usuarios'))
    else:
        return render_template('agregar_usuario.html')

@app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    if request.method == 'POST':
        # Obtener los datos del formulario
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']
        nombre = request.form['nombre']
        tipo_usuario = request.form['tipo_usuario']

        # Cifrar la contraseña
        contraseña_cifrada = generate_password_hash(contraseña)

        # Actualizar los datos en la base de datos
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor()
        query = "UPDATE usuarios SET usuario=%s, contraseña=%s, nombre=%s, tipo_usuario=%s WHERE id=%s"
        values = (usuario, contraseña_cifrada, nombre, tipo_usuario, id)
        cursor.execute(query, values)
        db.commit()

        return redirect(url_for('usuarios'))
    else:
        # Obtener los datos del usuario a editar desde la base de datos
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM usuarios WHERE id=%s"
        values = (id,)
        cursor.execute(query, values)
        usuario = cursor.fetchone()

        return render_template('editar_usuario.html', usuario=usuario)

@app.route('/eliminar_usuario/<int:id>', methods=['GET'])
@login_required
def eliminar_usuario(id):
    # Eliminar el usuario de la base de datos
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()
    query = "DELETE FROM usuarios WHERE id=%s"
    values = (id,)
    cursor.execute(query, values)
    db.commit()

    return redirect(url_for('usuarios'))

if __name__ == '__main__':
    app.run()