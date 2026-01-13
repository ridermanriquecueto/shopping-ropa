from flask import Flask, render_template, request, redirect, url_for, Response, flash
import os
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)

# --- CONFIGURACIÓN ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tienda.db'
app.config['UPLOAD_FOLDER'] = 'static/img'
# La secret_key es obligatoria para usar flash()
app.secret_key = 'shopping_ropa_puesto_129_130' 

db = SQLAlchemy(app)

# --- MODELO DE PRODUCTO ---
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.String(20), nullable=False)
    detalles = db.Column(db.String(200))
    imagen = db.Column(db.String(100))
    categoria = db.Column(db.String(50)) 

# --- SEGURIDAD ---
def check_auth(username, password):
    return username == 'admin' and password == 'admin'

def authenticate():
    return Response('Login Requerido', 401, {'WWW-Authenticate': 'Basic realm="Login Requerido"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Crear base de datos
with app.app_context():
    db.create_all()

# --- RUTA PÚBLICA (CLIENTES) ---
@app.route('/')
def index():
    productos = Producto.query.all()
    # Separamos para que el index no mezcle ropa de nene con adulto
    infantiles = [p for p in productos if p.categoria == 'infantil']
    adultos = [p for p in productos if p.categoria == 'adulto']
    return render_template('index.html', infantiles=infantiles, adultos=adultos)

# --- RUTAS DE ADMINISTRACIÓN (CRUD) ---

@app.route('/admin')
@requires_auth
def admin():
    productos = Producto.query.all()
    infantil = [p for p in productos if p.categoria == 'infantil']
    adulto = [p for p in productos if p.categoria == 'adulto']
    return render_template('admin.html', infantil=infantil, adulto=adulto)

@app.route('/add', methods=['POST'])
@requires_auth
def add_producto():
    nombre = request.form['nombre']
    precio = request.form['precio']
    detalles = request.form['detalles']
    categoria = request.form['categoria'] 
    file = request.files['imagen']
    
    if file:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        nuevo = Producto(nombre=nombre, precio=precio, detalles=detalles, imagen=filename, categoria=categoria)
        db.session.add(nuevo)
        db.session.commit()
        flash(f'✅ ¡"{nombre}" cargado con éxito!')
    return redirect(url_for('admin'))

@app.route('/editar/<int:id>')
@requires_auth
def edit_producto(id):
    prod = db.session.get(Producto, id)
    return render_template('editar.html', p=prod)

@app.route('/update/<int:id>', methods=['POST'])
@requires_auth
def update_producto(id):
    prod = db.session.get(Producto, id)
    if prod:
        prod.nombre = request.form['nombre']
        prod.precio = request.form['precio']
        prod.categoria = request.form['categoria']
        prod.detalles = request.form['detalles']
        
        file = request.files['imagen']
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            prod.imagen = filename
            
        db.session.commit()
        flash(f'💾 Actualizado: {prod.nombre}')
    return redirect(url_for('admin'))

@app.route('/delete/<int:id>')
@requires_auth
def delete_producto(id):
    prod = db.session.get(Producto, id)
    if prod:
        nombre_temp = prod.nombre
        db.session.delete(prod)
        db.session.commit()
        flash(f'🗑️ Eliminado: {nombre_temp}')
    return redirect(url_for('admin'))

if __name__ == "__main__":
    app.run(debug=True)