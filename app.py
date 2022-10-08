from operator import index
from optparse import Values
import os
import string
from flask import Flask, jsonify, render_template, flash, request, redirect, session, url_for
import utils
from db import get_db, close_db
from flask_session import Session
import sqlite3
from flask_cors import CORS


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'esto-es-una-clave-muy-secreta'
Session(app)
CORS(app)


@app.route('/', methods=('GET', 'POST'))
@app.route('/login', methods=('GET', 'POST'))
def login():
    print(request.method)
    try:
        # Si viene por post es que vienen datos del formulario por procesar
        if request.method == 'POST':
            db = get_db()
            error = None

            email = request.form['email']
            password = request.form['password']
            print(email, password)
            if not email:
                error = 'Debes ingresar el usuario'
                flash(error)
                return render_template('login.html')

            if not password:
                error = 'Contraseña Requerida'
                flash(error)
                return render_template('login.html')
            print(email, password)
            user = db.execute(
                'SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()

            close_db()

            if user is None:
                error = 'Usuario o contraseña invalidos'
            else:
                role = db.execute(
                    'SELECT rol FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
                if (user[3] == 'empleado'):
                    id_emp = db.execute(
                        'SELECT id FROM empleados WHERE id_user = ?', [user[0]]).fetchone()
                    session['id_emp'] = id_emp[0]
                close_db()

                session['role'] = role[0]
                print(session)
                return redirect('inicio')
            flash(error)

        # Si viene por Get es porque hubo un error y se renderiza o lo llamaron desde la url
        # Debere volver a mostrar el login.html
        return render_template('login.html')
    except:
        return render_template('404.html', role=session.get('role'))
        return f'Ha ocurrido un error'
        # return render_template('login.html')


@app.route('/inicio')
def inicio():

    if session.get('role') == 'admin':
        return render_template('home.html', role='admin')
    elif session.get('role') == 'superadmin':
        return render_template('home.html', role='superadmin')
    else:
        return render_template('home.html', role='empleado')


@app.route('/gestionarEmpleados')
def gestionarEmpleados():
    try:
        db = get_db()
        error = None
        empleados = db.execute(
            'SELECT * FROM empleados').fetchall()

        close_db()
        if session.get('role') == 'admin':
            return render_template('gestionarEmpleados.html', empleados=empleados, role='admin')
        elif session.get('role') == 'superadmin':
            return render_template('gestionarEmpleados.html', empleados=empleados, role='superadmin')

        flash(error)
    except:
        return render_template('404.html', role=session.get('role'))
        return f'Ha ocurrido un error'


@app.route('/gestionarAdministradores')
def gestionarAdministradores():
    try:
        if session.get('role') == 'superadmin':
            db = get_db()
            error = None
            admins = db.execute(
                'SELECT * FROM administradores').fetchall()
            close_db()
            # render_template('gestionarAdministradores.html',role='superadmin')
            for value in admins:
                print(value)
            # for i in range(0, len(admins)):
            #     print(admins[i])
            return render_template('gestionarAdministradores.html', admins=admins, role='superadmin')
            flash(error)
    except:
        return render_template('404.html', role=session.get('role'))
        return f'Ha ocurrido un error'


@app.route('/agregarEmpleado', methods=('GET', 'POST'))
def agregarEmpleado():
    # if session.get('role') == 'admin':
    #     return render_template('agregarEmpleado.html', role='admin')
    # elif session.get('role') == 'superadmin':
    #     return render_template('agregarEmpleado.html', role='superadmin')
    try:
        if request.method == 'POST':
            cedula = int(request.form['cedula'])
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            email = request.form['email']
            nacimiento = request.form['naci']
            direccion = request.form['direccion']
            telefono = request.form['telefono']
            sexo = request.form['sexo']
            estado_civil = request.form['estadocivil']
            ingreso = request.form['fechaingre']
            tipo_contrato = request.form['tipocont']
            termina = request.form['fechaterm']
            cargo = request.form['cargo']
            dependencia = request.form['dependencia']
            salario = request.form['salario']
            error = None

            if not utils.isEmailValid(email):
                error = 'Correo no valido'
                flash(error)
                return render_template('agregarEmplaedo.html', role=session.get('role'))

            db = get_db()

            error = None
            cur = db.execute(
                'insert into users (email, password, rol) values (?,?,?)', [
                    email, cedula, 'empleado']
            )
            newEmplId = cur.lastrowid
            db.commit()
            print(newEmplId)
            db.execute('insert into empleados (cedula, nombres, apellido,direccion,email,telefono,fecha_nacimiento,sexo,estado_civil,id_user,fecha_ingreso,tipo_contrato,fecha_term_contrato,cargo,dependencia,salario) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                       [cedula, nombre, apellido, direccion, email, telefono, nacimiento, sexo, estado_civil,
                           newEmplId, ingreso, tipo_contrato, termina, cargo, dependencia, salario]
                       )
            db.commit()

            db.close()
            print(newEmplId)

            mensaje='Empleado Agregado correctamente'
            return render_template('exito.html', role=session.get('role'),mensaje=mensaje)
        else:
            return render_template('agregarEmpleado.html', role=session.get('role'))
    except Exception as e:
        return render_template('404.html', role=session.get('role'))
        return e


@app.route('/agregarAdministrador', methods=('GET', 'POST'))
def agregarAdministrador():
    try:
        if request.method == 'POST':
            cedula = int(request.form['cedula'])
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            email = request.form['email']
            nacimiento = request.form['naci']
            direccion = request.form['direccion']
            telefono = request.form['telefono']
            sexo = request.form['sexo']
            estado_civil = request.form['estadocivil']
            error = None

            if not utils.isEmailValid(email):
                error = 'Correo no valido'
                flash(error)
                return render_template('agregarAdministrador.html', role=session.get('role'))

            db = get_db()

            error = None
            cur = db.execute(
                'insert into users (email, password, rol) values (?,?,?)', [
                    email, cedula, 'admin']
            )
            newAdminId = cur.lastrowid
            db.commit()
            print(newAdminId)
            db.execute('insert into administradores (cedula, nombres, apellido,direccion,email,telefono,fecha_nacimiento,sexo,estado_civil,id_user) values (?,?,?,?,?,?,?,?,?,?)',
                       [cedula, nombre, apellido, direccion, email, telefono,
                           nacimiento, sexo, estado_civil, newAdminId]
                       )
            db.commit()
            # id = db.lastrowid

            db.close()
            print(newAdminId)

            mensaje= 'Administrador agregado correctamente'
            return render_template('exito.html', role=session.get('role'),mensaje=mensaje)
        
        return render_template('agregarAdministrador.html', role=session.get('role'))
    except Exception as e:
        return render_template('404.html', role=session.get('role'))
        return e

    if session.get('role') == 'admin':
        return render_template('agregarAdministrador.html', role='admin')
    elif session.get('role') == 'superadmin':
        return render_template('agregarAdministrador.html', role='superadmin')


@app.route('/informacionEmpleado/<id>')
def informacionEmpleado(id):
    try:
        db = get_db()
        error = None
        empleado = db.execute(
            'SELECT * FROM empleados where id= (?)', [id]).fetchone()

        close_db()
        db.close()
        print(empleado)
        # fecha_nac=datetime.datetime.strptime(empleado[12], "%d/%m/%Y").strftime("%Y-%m-%d")
        # fecha_ingr=datetime.datetime.strptime(empleado[9], "%d/%m/%Y").strftime("%Y-%m-%d")
        # fecha_term=datetime.datetime.strptime(empleado[10], "%d/%m/%Y").strftime("%Y-%m-%d")

        # ,fecha_nac=fecha_nac,fecha_ingre=fecha_ingr,fecha_term=fecha_term)
        return render_template('inforEmpleado.html', role=session.get('role'), empleado=empleado)

        # elif request.method == 'POST':

    except Exception as e:
        print(e)
        return render_template('404.html', role=session.get('role'))

    if session.get('role') == 'empleado':
        return render_template('inforEmpleado.html', role='empleado')
    elif session.get('role') == 'admin':
        return render_template('inforEmpleado.html', role='admin')
    else:
        return render_template('inforEmpleado.html', role='superadmin')


@app.route('/calificarEmpleado')
def calificarEmpleado():
    if session.get('role') == 'admin':
        return render_template('calificarEmpleado.html', role='admin')
    else:
        return render_template('calificarEmpleado.html', role='superadmin')

# id=db.cursor().lastrowid


@app.route('/gestionarEmpleados/eliminar/<id>')
def eliminar_empleado(id):
    try:
        db = get_db()
        error = None
        user=db.execute('SELECT id_user FROM empleados WHERE id = (?)', [id]).fetchone()
        user=user[0]
        print(user)
        db.execute('DELETE FROM empleados WHERE id = (?)', [id])
        db.commit()
        db.execute('DELETE FROM users WHERE id = (?)', [user])
        db.commit()
        db.close()
        flash("Empleado eliminado correctamente")
        return redirect(url_for('gestionarEmpleados'))

    except:
        return render_template('404.html', role=session.get('role'))


@app.route('/gestionarAdministradores/eliminar/<id>')
def eliminar_administrador(id):
    try:
        db = get_db()
        error = None
        ad=db.execute('SELECT id_user FROM administradores WHERE id = (?)', [id]).fetchone()
        ad=ad[0]
        db.execute('DELETE FROM administradores WHERE id = (?)', [id])
        db.commit()
        db.execute('DELETE FROM users WHERE id = (?)', [ad])
        db.commit()
        db.close()
        flash("Administrador eliminado correctamente")
        return redirect(url_for('gestionarAdministradores'))

    except:
        return render_template('404.html', role=session.get('role'))


@app.route('/gestionarEmpleados/editar/<id>', methods=('GET', 'POST'))
def editarEmpleado(id):
    # import datetime
    print(request.method)
    print(request.args)
    try:
        if request.method == "POST":
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            email = request.form['email']
            direccion = request.form['direccion']
            telefono = request.form['telefono']
            estado_civil = request.form['estadocivil']
            ingreso = request.form['fechaingre']
            tipo_contrato = request.form['tipocont']
            termina = request.form['fechaterm']
            cargo = request.form['cargo']
            dependencia = request.form['dependencia']
            salario = request.form['salario']
            print(nombre, apellido, email, direccion, telefono, estado_civil,
                  ingreso, tipo_contrato, termina, cargo, dependencia, salario)
            error = None

            if not utils.isEmailValid(email):
                error = 'Correo no valido'
                flash(error)
                return render_template('gestionarEmpleados.html', role=session.get('role'))

            print(id)
            db = get_db()
            mydb = db.cursor()
            sql = "update empleados set nombres= (?), apellido= (?), email= (?), cargo = (?), dependencia = (?), tipo_contrato=(?), fecha_ingreso=(?), fecha_term=(?), direccion=(?), telefono=(?), salario=(?), estado_civil=(?) where id = (?)"
            val = (nombre, apellido, email, cargo, dependencia, tipo_contrato,
                   ingreso, termina, direccion, telefono, salario, estado_civil, id)
            mydb.execute("update empleados set nombres= (?), apellido= (?), email= (?), cargo = (?), dependencia = (?), tipo_contrato=(?), fecha_ingreso=(?), fecha_term_contrato=(?), direccion=(?), telefono=(?), salario=(?), estado_civil=(?) where id = (?)", [
                         nombre, apellido, email, cargo, dependencia, tipo_contrato, ingreso, termina, direccion, telefono, salario, estado_civil, id])
            db.commit()
            db.close()

            mensaje= 'Empleado modificado correctamente'
            return render_template('exito.html', role=session.get('role'),mensaje=mensaje)
        
        else:
            db = get_db()
            error = None
            empleado = db.execute(
                'SELECT * FROM empleados where id= (?)', [id]).fetchone()

            close_db()
            db.close()
            print(empleado)
            
            return render_template('editarEmpleado.html', role=session.get('role'), empleado=empleado)

        # elif request.method == 'POST':

    except Exception as e:
        print(e)
        return render_template('404.html', role=session.get('role'))


@app.route('/gestionarAdministradores/editar/<id>', methods=('GET', 'POST'))
def editarAdministrador(id):
    # import datetime
    print(request.method)
    print(request.args)
    try:
        if request.method == "POST":
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            email = request.form['email']
            direccion = request.form['direccion']
            telefono = request.form['telefono']
            estado_civil = request.form['estadocivil']

            error = None

            if not utils.isEmailValid(email):
                error = 'Correo no valido'
                flash(error)
                return render_template('gestionarEmpleados.html', role=session.get('role'))

            print(id)
            db = get_db()
            mydb = db.cursor()
            mydb.execute("update administradores set nombres= (?), apellido= (?), email= (?), direccion=(?), telefono=(?),  estado_civil=(?) where id = (?)", [
                         nombre, apellido, email, direccion, telefono, estado_civil, id])
            db.commit()
            db.close()

            mensaje='Administrador modificado correctamente'
            return render_template('exito.html', role=session.get('role'),mensaje=mensaje)

        else:
            db = get_db()
            error = None
            admin = db.execute(
                'SELECT * FROM administradores where id= (?)', [id]).fetchone()

            close_db()
            db.close()
            print(admin)
            # fecha_nac=datetime.datetime.strptime(empleado[12], "%d/%m/%Y").strftime("%Y-%m-%d")
            # fecha_ingr=datetime.datetime.strptime(empleado[9], "%d/%m/%Y").strftime("%Y-%m-%d")
            # fecha_term=datetime.datetime.strptime(empleado[10], "%d/%m/%Y").strftime("%Y-%m-%d")

            # ,fecha_nac=fecha_nac,fecha_ingre=fecha_ingr,fecha_term=fecha_term)
            return render_template('editarAdministrador.html', role=session.get('role'), admin=admin)

        # elif request.method == 'POST':

    except Exception as e:
        print(e)
        return render_template('404.html', role=session.get('role'))


@app.route('/gestionarAdministradores/infoAdministrador/<id>')
def infoAdministrador(id):
    # import datetime
    print(request.method)
    print(request.args)
    try:
        db = get_db()
        error = None
        admin = db.execute(
            'SELECT * FROM administradores where id= (?)', [id]).fetchone()

        close_db()
        db.close()
        print(admin)
        # fecha_nac=datetime.datetime.strptime(empleado[12], "%d/%m/%Y").strftime("%Y-%m-%d")
        # fecha_ingr=datetime.datetime.strptime(empleado[9], "%d/%m/%Y").strftime("%Y-%m-%d")
        # fecha_term=datetime.datetime.strptime(empleado[10], "%d/%m/%Y").strftime("%Y-%m-%d")

        # ,fecha_nac=fecha_nac,fecha_ingre=fecha_ingr,fecha_term=fecha_term)
        return render_template('verAdministrador.html', role=session.get('role'), admin=admin)

    except Exception as e:
        print(e)
        return render_template('404.html', role=session.get('role'))
