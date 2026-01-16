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
    # 1. Registro de acceso (esto lo dejamos igual porque funciona bien)
    import datetime
    fecha = (datetime.datetime.now() - datetime.timedelta(hours=3)).strftime("%d/%m/%Y %H:%M:%S")
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    with open("accesos_vendedoras.txt", "a", encoding='utf-8') as f:
        f.write(f"Vendedora entró: {fecha} - IP: {ip}\n")

    # 2. Obtener todos los productos para la tabla
    productos = Producto.query.all()
    
    # 3. SUMA DE STOCK REAL (Asegurate de que los nombres coincidan con tu HTML)
    # Cambiamos 'total_infantil' por 'infantil' para que el HTML lo reconozca
    stock_infantil = db.session.query(func.sum(Producto.stock)).filter(
        Producto.categoria.in_(['Nenes', 'Nenas', 'Infantil General'])
    ).scalar() or 0

    stock_adulto = db.session.query(func.sum(Producto.stock)).filter(
        Producto.categoria.in_(['Adulto', 'Puesto 130 - Adulto'])
    ).scalar() or 0

    stock_general = db.session.query(func.sum(Producto.stock)).scalar() or 0

    # 4. Enviar al HTML con los nombres de variable correctos
    return render_template('admin.html', 
                           productos=productos, 
                           infantil=stock_infantil,  # Aquí está la clave
                           adulto=stock_adulto,      # Aquí también
                           total=stock_general)      # Y aquí

@app.route('/add', methods=['POST'])
@requires_auth
def add_producto():
    nombre = request.form['nombre']
    precio = request.form['precio']
    categoria = request.form['categoria']
    stock = request.form.get('stock', 1) 
    es_oferta = 'oferta' in request.form
    
    # 1. Crear el producto primero (para obtener el ID)
    nuevo_p = Producto(
        nombre=nombre, 
        precio=float(precio), 
        categoria=categoria, 
        stock=int(stock),
        oferta=es_oferta
    )
    db.session.add(nuevo_p)
    db.session.flush() # ID generado

    # 2. Procesar fotos individuales (file1 a file6)
    mapeo = {
        'file1': 'imagen', 'file2': 'img2', 'file3': 'img3',
        'file4': 'img4', 'file5': 'img5', 'file6': 'img6'
    }

    for input_name, col_db in mapeo.items():
        archivo = request.files.get(input_name)
        if archivo and archivo.filename != '':
            ext = os.path.splitext(archivo.filename)[1]
            nombre_foto = f"prod_{nuevo_p.id}_{input_name}{ext}"
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_foto))
            setattr(nuevo_p, col_db, nombre_foto)

    # 3. PROCESAR CARGA POR LOTE / CÁMARA (fotos_masivas)
    # Esto llena los huecos que hayan quedado vacíos arriba
    fotos_masivas = request.files.getlist('fotos_masivas')
    columnas_totales = ['imagen', 'img2', 'img3', 'img4', 'img5', 'img6']
    
    if fotos_masivas and fotos_masivas[0].filename != '':
        for f in fotos_masivas:
            # Buscamos la primera columna que esté vacía
            for col in columnas_totales:
                if not getattr(nuevo_p, col): 
                    ext = os.path.splitext(f.filename)[1]
                    nom_m = f"prod_{nuevo_p.id}_{col}_cam{ext}"
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], nom_m))
                    setattr(nuevo_p, col, nom_m)
                    break # Pasamos a la siguiente foto del lote

    db.session.commit()
    flash('✅ Producto y fotos cargados exitosamente')
    return redirect(url_for('admin'))

@app.route('/editar/<int:id>')
@requires_auth
def editar(id):
    producto = Producto.query.get_or_404(id)
    return render_template('editar.html', p=producto)


@app.route('/update/<int:id>', methods=['POST'])
@requires_auth
def update(id):
    p = Producto.query.get_or_404(id)
    
    # 1. Actualizar textos básicos
    p.nombre = request.form.get('nombre')
    p.precio = float(request.form.get('precio'))
    p.stock = int(request.form.get('stock'))
    p.categoria = request.form.get('categoria')
    p.oferta = 'oferta' in request.form

    # 2. Lógica para BORRAR fotos (Antes de subir las nuevas)
    columnas_galeria = ['img2', 'img3', 'img4', 'img5', 'img6']
    for col in columnas_galeria:
        if request.form.get(f'borrar_{col}'):
            # Si el usuario tildó "Borrar", ponemos la columna en blanco
            setattr(p, col, None)

    # 3. Procesar Subida de fotos individuales (file1 a file6)
    mapeo_fotos = {
        'file1': 'imagen',
        'file2': 'img2',
        'file3': 'img3',
        'file4': 'img4',
        'file5': 'img5',
        'file6': 'img6'
    }

    for input_nombre, columna_db in mapeo_fotos.items():
        archivo = request.files.get(input_nombre)
        if archivo and archivo.filename != '':
            # Generamos nombre: prod_ID_campo.jpg
            extension = os.path.splitext(archivo.filename)[1]
            nombre_final = f"prod_{id}_{input_nombre}{extension}"
            
            # Guardamos el archivo físico
            archivo.save(os.path.join('static/img', nombre_final))
            
            # Guardamos en la base de datos
            setattr(p, columna_db, nombre_final)

    # 4. Procesar Carga Masiva (WhatsApp)
    # Solo llena las columnas que estén vacías después de los pasos anteriores
    fotos_masivas = request.files.getlist('fotos_masivas')
    if fotos_masivas and fotos_masivas[0].filename != '':
        for f in fotos_masivas:
            for col in columnas_galeria:
                if not getattr(p, col): # Si el espacio está vacío
                    ext = os.path.splitext(f.filename)[1]
                    nom_m = f"prod_{id}_{col}_masiva{ext}"
                    f.save(os.path.join('static/img', nom_m))
                    setattr(p, col, nom_m)
                    break # Salta a la siguiente foto masiva

    db.session.commit()
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