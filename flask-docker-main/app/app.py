import os
from flask import Flask, flash, render_template, redirect, url_for, request, session
from dao.DAOUsuario import DAOUsuario 

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mys3cr3tk3y')

db = DAOUsuario()
ruta = '/usuario'

@app.route('/')
def inicio():
    # Si ya hay sesión activa, redirige a usuarios
    if 'user' in session:
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        usuarios = db.read(None)
        # Busca usuario por email
        user = next((u for u in usuarios if u[3] == email), None)
        if user:
            session['user'] = user[1]  # Guarda nombre de usuario en sesión
            flash(f'Bienvenido {user[1]}')
            return redirect(url_for('index'))
        else:
            flash('Email no registrado')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Sesión cerrada')
    return redirect(url_for('inicio'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = {
            'nombre': request.form.get('nombre'),
            'telefono': request.form.get('telefono'),
            'email': request.form.get('email')
        }
        if db.insert(data):
            flash('Usuario registrado correctamente')
            return redirect(url_for('login'))
        else:
            flash('Error al registrar usuario')
    return render_template('register.html')

# Rutas protegidas (solo si está el usuario en sesión)
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Por favor inicia sesión primero')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route(ruta + '/')
@login_required
def index():
    data = db.read(None)
    return render_template('usuario/index.html', data=data)

@app.route(ruta + '/add/')
@login_required
def add():
    return render_template('usuario/add.html')

@app.route(ruta + '/addusuario', methods=['POST'])
@login_required
def addusuario():
    if 'save' in request.form:
        if db.insert(request.form):
            flash("Nuevo usuario creado")
        else:
            flash("ERROR al crear usuario")
    return redirect(url_for('index'))

@app.route(ruta + '/update/<int:id>/')
@login_required
def update(id):
    data = db.read(id)
    if not data:
        return redirect(url_for('index'))
    session['update'] = id
    return render_template('usuario/update.html', data=data)

@app.route(ruta + '/updateusuario', methods=['POST'])
@login_required
def updateusuario():
    if 'update' in request.form:
        if db.update(session.get('update'), request.form):
            flash('Se actualizó correctamente')
        else:
            flash('ERROR en actualizar')
        session.pop('update', None)
    return redirect(url_for('index'))

@app.route(ruta + '/delete/<int:id>/')
@login_required
def delete(id):
    data = db.read(id)
    if not data:
        return redirect(url_for('index'))
    session['delete'] = id
    return render_template('usuario/delete.html', data=data)

@app.route(ruta + '/deleteusuario', methods=['POST'])
@login_required
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
