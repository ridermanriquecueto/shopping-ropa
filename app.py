from flask import Flask, render_template, request, redirect, url_for, Response, flash, session
from sqlalchemy import func
import os
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.utils import secure_filename
import datetime

app = Flask(__name__)

# --- CONFIGURACIÓN ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tienda.db'
app.config['UPLOAD_FOLDER'] = 'static/img'
app.secret_key = 'shopping_ropa_puesto_129_130' 

db = SQLAlchemy(app)

# --- MODELO DE PRODUCTO ---
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50), nullable=False, default='Adulto')
    stock = db.Column(db.Integer, default=1)
    imagen = db.Column(db.String(100))
    img2 = db.Column(db.String(100), nullable=True)
    img3 = db.Column(db.String(100), nullable=True)
    img4 = db.Column(db.String(100), nullable=True)
    img5 = db.Column(db.String(100), nullable=True)
    img6 = db.Column(db.String(100), nullable=True)
    oferta = db.Column(db.Boolean, default=False)

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

 
# --- RUTA PÚBLICA (CLIENTES) ---
@app.route('/')
def index():
    productos = Producto.query.all()
    infantiles = [p for p in productos if p.categoria in ['Nenes', 'Nenas', 'Infantil']]
    adultos = [p for p in productos if p.categoria in ['Adulto', 'Adultos']]
    return render_template('index.html', infantiles=infantiles, adultos=adultos)

# --- RUTAS DE ADMINISTRACIÓN ---

@app.route('/admin')
@requires_auth
def admin():
    # 1. Crea la fecha
    import datetime
    fecha = (datetime.datetime.now() - datetime.timedelta(hours=3)).strftime("%d/%m/%Y %H:%M:%S")
    
    # 2. Atrapa la IP (identidad del celular/compu)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # 3. Lo escribe en el "cuaderno" (archivo .txt)
    with open("accesos_vendedoras.txt", "a") as f:
        f.write(f"Vendedora entró: {fecha} - IP: {ip}\n")

    productos = Producto.query.all()
    
    # SUMA DE UNIDADES (Stock real)
    total_infantil = db.session.query(func.sum(Producto.stock)).filter(Producto.categoria.in_(['Nenes', 'Nenas', 'Infantil'])).scalar() or 0
    total_adulto = db.session.query(func.sum(Producto.stock)).filter(Producto.categoria.in_(['Adulto', 'Adultos'])).scalar() or 0
    total_general = db.session.query(func.sum(Producto.stock)).scalar() or 0

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
    stock = request.form.get('stock', 1) 
    es_oferta = True if request.form.get('oferta') else False
    
    # 1. Foto Principal
    f_principal = request.files['imagen']
    filename_p = secure_filename(f_principal.filename)
    f_principal.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_p))
    
    # 2. Fotos Extras
    extras = {}
    for i in range(2, 7):
        campo = f'img{i}'
        file = request.files.get(campo)
        if file and file.filename != '':
            fname = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
            extras[campo] = fname
        else:
            extras[campo] = None

    # 3. Guardar en la Base de Datos
    nuevo_p = Producto(
        nombre=nombre, 
        precio=float(precio), 
        categoria=categoria, 
        stock=int(stock),
        imagen=filename_p,
        img2=extras['img2'], img3=extras['img3'], img4=extras['img4'],
        img5=extras['img5'], img6=extras['img6'],
        oferta=es_oferta
    )
    
    db.session.add(nuevo_p)
    db.session.commit()
    flash('✅ Producto cargado exitosamente')
    return redirect(url_for('admin'))

@app.route('/editar/<int:id>')
@requires_auth
def editar(id):
    producto = Producto.query.get_or_404(id)
    return render_template('editar.html', p=producto)

@app.route('/update/<int:id>', methods=['POST'])
@requires_auth
def update(id):
    producto = Producto.query.get_or_404(id)
    producto.nombre = request.form['nombre']
    producto.precio = float(request.form['precio'])
    producto.categoria = request.form['categoria']
    producto.stock = int(request.form.get('stock', producto.stock))
    producto.oferta = True if request.form.get('oferta') else False
    producto.stock = request.form.get('stock')
    
    if 'imagen' in request.files:
        file = request.files['imagen']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            producto.imagen = filename
            
    db.session.commit()
    flash('✅ Producto actualizado')
    return redirect(url_for('admin'))

@app.route('/delete/<int:id>')
@requires_auth
def delete_producto(id):
    prod = Producto.query.get(id)
    if prod:
        db.session.delete(prod)
        db.session.commit()
        flash('🗑️ Producto eliminado')
    return redirect(url_for('admin'))
@app.route('/logout')
def logout():
    session.clear() 
    # Como usas Basic Auth, al redirigir al index el navegador ya no mandará las credenciales
    return redirect(url_for('index'))   

if __name__ == "__main__":
    # 1. Primero creamos las tablas (esto soluciona el error del stock)
    with app.app_context():
        db.create_all()
    
    # 2. Después iniciamos el servidor
    app.run(debug=True)