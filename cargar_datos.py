from app import app, db, Producto

# Los datos que ya tenías
infantiles = [
    {"nombre": "Ropa de Baño Nena", "precio": "1800", "img": "ropa de baño de nenas.jpeg", "detalles": "Talles 4 al 16"},
    {"nombre": "Short Adidas Nene", "precio": "1500", "img": "short adidas nenes.jpeg", "detalles": "Talles 4 al 16"},
    {"nombre": "Short Jordan Nena", "precio": "1600", "img": "short jordan nenas.jpeg", "detalles": "Talles 4 al 16"},
    {"nombre": "Short Nena Verano", "precio": "1300", "img": "short nena.jpeg", "detalles": "Talles 4 al 16"},
    {"nombre": "Vestido sin Botones", "precio": "2100", "img": "vestido sin botones neneas.jpeg", "detalles": "Talles 4 al 16"},
    {"nombre": "Bermuda Nene", "precio": "1500", "img": "bermudas nenes.jpeg", "detalles": "Talles 4 al 16"}
]

adultos = [
    {"nombre": "Remera Waffle", "precio": "1800", "img": "remeras tela wafle.jpg", "detalles": "S al XL"},
    {"nombre": "Mallas Adulto", "precio": "2500", "img": "ropa de baño .jpg", "detalles": "M al XXL"},
    {"nombre": "Short Gabardina", "precio": "1500", "img": "short .jpeg", "detalles": "38 al 48"}
]

def cargar():
    with app.app_context():
        # Cargamos Infantiles
        for p in infantiles:
            nuevo = Producto(nombre=p['nombre'], precio=p['precio'], detalles=p['detalles'], imagen=p['img'], categoria='infantil')
            db.session.add(nuevo)
        
        # Cargamos Adultos
        for p in adultos:
            nuevo = Producto(nombre=p['nombre'], precio=p['precio'], detalles=p['detalles'], imagen=p['img'], categoria='adulto')
            db.session.add(nuevo)
            
        db.session.commit()
        print("✅ ¡Datos cargados con éxito en la base de datos!")

if __name__ == "__main__":
    cargar()