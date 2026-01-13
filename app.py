from flask import Flask, render_template, request, redirect, url_for, Response, flash
import os
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)

# --- CONFIGURACIÓN ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tienda.db'
app.config['UPLOAD_FOLDER'] = 'static/img'
app.secret_key = 'shopping_ropa_puesto_129_130' 

db = SQLAlchemy(app)

# --- MODELO DE PRODUCTO (Ajustado sin detalles) ---
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50), nullable=False, default='Adulto')
    imagen = db.Column(db.String(100))

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

with app.app_context():
    db.create_all()

# --- RUTA PÚBLICA (CLIENTES) ---
@app.route('/')
def index():
    productos = Producto.query.all()
    # Filtramos para enviar las listas correctas al HTML
    # Buscamos 'Nenes' o 'Nenas' para la sección infantil
    infantiles = [p for p in productos if p.categoria in ['Nenes', 'Nenas']]
    adultos = [p for p in productos if p.categoria == 'Adulto']
    return render_template('index.html', infantiles=infantiles, adultos=adultos)

# --- RUTAS DE ADMINISTRACIÓN ---

@app.route('/admin')
@requires_auth
def admin():
    productos = Producto.query.all()
    
    # Contadores
    total_infantil = Producto.query.filter(Producto.categoria.in_(['Nenes', 'Nenas', 'infantil'])).count()
    total_adulto = Producto.query.filter(Producto.categoria.in_(['Adulto', 'adulto'])).count()
    total_general = len(productos)

    return render_template('admin.html', 
                           productos=productos, 
                           total_infantil=total_infantil, 
                           total_adulto=total_adulto,
                           total_general=total_general)
@app.route('/add', methods=['POST'])
@requires_auth
def add_producto():
    nombre = request.form['nombre']
    precio = request.form['precio']
    categoria = request.form['categoria'] 
    file = request.files['imagen']
    
    if file:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        nuevo = Producto(nombre=nombre, precio=precio, imagen=filename, categoria=categoria)
        db.session.add(nuevo)
        db.session.commit()
        flash(f'✅ ¡"{nombre}" cargado con éxito!')
    return redirect(url_for('admin'))

    @app.route('/update/<int:id>', methods=['POST'])
    def update_producto(id):
        prod = Producto.query.get(id)
        if prod:
            prod.nombre = request.form['nombre']
            prod.precio = request.form['precio']
            prod.categoria = request.form['categoria']
            
            file = request.files['imagen']
            if file and file.filename != '':
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                prod.imagen = filename
                
            db.session.commit()
        return redirect(url_for('admin'))
    # RUTA 1: Muestra el formulario de edición (El que te da el error 404)
@app.route('/editar/<int:id>')
@requires_auth
def editar(id):
    # Buscamos el producto por su ID
    producto = Producto.query.get_or_404(id)
    return render_template('editar.html', p=producto)

# RUTA 2: Recibe los datos del formulario y los guarda
@app.route('/update/<int:id>', methods=['POST'])
@requires_auth
def update(id):
    producto = Producto.query.get_or_404(id)
    
    producto.nombre = request.form['nombre']
    producto.precio = request.form['precio']
    producto.categoria = request.form['categoria']
    
    # Manejo de la imagen opcional
    if 'imagen' in request.files:
        file = request.files['imagen']
        if file.filename != '':
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            producto.imagen = filename
            
    db.session.commit()
    flash('✅ Producto actualizado correctamente')
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