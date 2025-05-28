import os
from flask import Flask, flash, render_template, redirect, url_for, request, session
from dao.DAOUsuario import DAOUsuario 

app = Flask(__name__, template_folder='templates', static_folder='static')

# Configuración de clave secreta (puede venir de variable de entorno o fallback)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mys3cr3tk3y')

db = DAOUsuario()
ruta = '/usuario'

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route(ruta + '/')
def index():
    data = db.read(None)
    return render_template('usuario/index.html', data=data)

@app.route(ruta + '/add/')
def add():
    return render_template('usuario/add.html')

@app.route(ruta + '/addusuario', methods=['POST'])
def addusuario():
    if 'save' in request.form:
        if db.insert(request.form):
            flash("Nuevo usuario creado")
        else:
            flash("ERROR al crear usuario")
    return redirect(url_for('index'))

@app.route(ruta + '/update/<int:id>/')
def update(id):
    data = db.read(id)
    if not data:
        return redirect(url_for('index'))
    session['update'] = id
    return render_template('usuario/update.html', data=data)

@app.route(ruta + '/updateusuario', methods=['POST'])
def updateusuario():
    if 'update' in request.form:
        if db.update(session.get('update'), request.form):
            flash('Se actualizó correctamente')
        else:
            flash('ERROR en actualizar')
        session.pop('update', None)
    return redirect(url_for('index'))

@app.route(ruta + '/delete/<int:id>/')
def delete(id):
    data = db.read(id)
    if not data:
        return redirect(url_for('index'))
    session['delete'] = id
    return render_template('usuario/delete.html', data=data)

@app.route(ruta + '/deleteusuario', methods=['POST'])
def deleteusuario():
    if 'delete' in request.form:
        if db.delete(session.get('delete')):
            flash('Usuario eliminado')
        else:
            flash('ERROR al eliminar')
        session.pop('delete', None)
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
