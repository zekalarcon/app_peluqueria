__author__ = "Ezequiel Alarcon"
__email__ = "zekalarcon@gmail.com"


from flask import Flask
from flask import render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, update
from sqlalchemy.orm import relationship
import datetime


#Sqlite Conexion

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/peluqueria.db'
db = SQLAlchemy(app)

# Settings

app.secret_key = 'mysecretkey'

# Creo tablas

class Operaciones(db.Model):
    __tablename__ = 'operaciones'
    id = db.Column(db.Integer, primary_key=True )
    fecha = db.Column(db.DateTime, nullable=False)
    operacion = db.Column(db.String, nullable=False)
    nombre_cliente = db.Column(db.String, nullable=False)
    telefono = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    empleado= db.Column(db.String, nullable=False)
    stock = db.relationship("Stock", cascade='all,delete', backref='operaciones')
    
    def __repr__(self):
        if len(self.stock) == 0:
            return f'Fecha: {self.fecha.strftime("%Y-%m-%d %H:%M:%S")}, Operacion: {self.operacion}, Nombre cliente: {self.nombre_cliente}, Telefono: {self.telefono}, Precio: {self.precio}, Empleado: {self.empleado}'
        else:    
            return f'Fecha: {self.fecha.strftime("%Y-%m-%d %H:%M:%S")}, Operacion: {self.operacion}, Nombre cliente: {self.nombre_cliente}, Telefono: {self.telefono}, Precio: {self.precio}, Empleado: {self.empleado}, {self.stock}'

class Stock(db.Model):
    _tablename__ = 'stock'
    id = db.Column(db.Integer, primary_key=True )
    fecha = db.Column(db.DateTime)
    producto = db.Column(db.String, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    accion = db.Column(db.String)
    trabajo_id = db.Column(db.Integer, ForeignKey('operaciones.id', ondelete='CASCADE'))  

    def __repr__(self):
        return f'Producto: {self.producto} Cantidad: {self.cantidad}'


# Drop tablas / Creo tablas

#db.drop_all()
#db.create_all()



# //////////////////////////////////////// INDEX //////////////////////////////////////////////////////////



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/agregar_trabajo', methods = ['POST'])
def agregar_trabajo():
    if request.method == 'POST':

        operaciones = Operaciones(fecha=datetime.datetime.now(),
                                  operacion=request.form['operacion'].upper(),
                                  nombre_cliente = request.form['nombre_cliente'].upper(),
                                  telefono = request.form['telefono_cliente'],
                                  precio = request.form['precio'],
                                  empleado = request.form['empleado'].upper())

        db.session.add(operaciones)  
        db.session.commit()          
    
        flash('Operacion guardada')

        return redirect(url_for('index'))


@app.route('/agregar_producto', methods = ['POST'])
def agregar_producto():
    if request.method == 'POST':

        operaciones_id = db.session.query(Operaciones.id).order_by(Operaciones.id.desc()).first()
        fecha = db.session.query(Operaciones.fecha).order_by(Operaciones.fecha.desc()).first()
        print(fecha)
        producto = Stock(
                         producto = request.form['producto_stock'].upper(),
                         cantidad = request.form['cantidad_stock'],
                         accion = 'EGRESO', trabajo_id = operaciones_id[0])

        db.session.add(producto)  
        db.session.commit()          
        
        flash('Producto agregado')

        return redirect(url_for('index'))


# ////////////////////////////////////////INFO CLIENTE///////////////////////////////////////////////////////////


@app.route('/cliente')
def cliente():

    return render_template('cliente.html')


@app.route('/info_cliente', methods = ['POST'])
def info_cliente():
    
    data = db.session.query(Operaciones).filter(Operaciones.nombre_cliente == request.form['cliente'].upper()).all()
    
    return render_template('cliente.html', cliente = data)    


@app.route('/delete/<string:data>')
def delete_cliente(data): 

    fecha = data[7:26]

    query = db.session.query(Operaciones).filter(Operaciones.fecha.startswith(fecha)).first()
    db.session.delete(query)
    db.session.commit()
    
    flash('Cliente borrado satisfactoriamente') 

    return render_template('cliente.html')


@app.route('/edit/<string:data>')
def editar_cliente(data):

    fecha = data[7:26]
    
    id_cliente = db.session.query(Operaciones.id).filter(Operaciones.fecha.startswith(fecha)).first()
    operacion =  db.session.query(Operaciones.operacion).filter(Operaciones.fecha.startswith(fecha)).first()
    nombre =  db.session.query(Operaciones.nombre_cliente).filter(Operaciones.fecha.startswith(fecha)).first()
    telefono =  db.session.query(Operaciones.telefono).filter(Operaciones.fecha.startswith(fecha)).first()
    precio = db.session.query(Operaciones.precio).filter(Operaciones.fecha.startswith(fecha)).first()
    empleado = db.session.query(Operaciones.empleado).filter(Operaciones.fecha.startswith(fecha)).first()
    productos =  db.session.query(Stock.producto).filter(Stock.trabajo_id == id_cliente[0]).all()
    cantidad = db.session.query(Stock.cantidad).filter(Stock.trabajo_id == id_cliente[0]).all()

    dicc = dict(zip(productos,cantidad))

    return render_template('editar_cliente.html', id = id_cliente, operacion = operacion, 
                            nombre = nombre, telefono = telefono, precio = precio, 
                            empleado = empleado, producto=dicc)    
    

@app.route('/update/<id>', methods = ['POST'])
def update_cliente(id):
    if request.method == 'POST':
        
        producto = request.form.getlist('producto')
        cantidad = request.form.getlist('cantidad')
        
        dicc = dict(zip(producto,cantidad))
        
        del dicc['']
               
        query = db.session.query(Operaciones).filter(Operaciones.id == id).first()
        db.session.delete(query)
        db.session.commit()

        
        operaciones = Operaciones(fecha=datetime.datetime.now(),
                                operacion=request.form['operacion'].upper(),
                                nombre_cliente = request.form['nombre_cliente'].upper(),
                                telefono = request.form['telefono_cliente'],
                                precio = request.form['precio'],
                                empleado = request.form['empleado'])

        db.session.add(operaciones)  
        db.session.commit() 

        if dicc:
            for key, value in dicc.items():
        
                producto = Stock(
                                producto = key.upper(),
                                cantidad = value,
                                accion = 'EGRESO', trabajo_id = id)
                
                db.session.add(producto)  
                db.session.commit()

            flash('Cliente Actualizado Satisfactoriamente')       
            return redirect(url_for('index'))

        else:                  
            flash('Cliente Actualizado Satisfactoriamente')       
            return redirect(url_for('index')) 



# ////////////////////////////////////////STOCK/////////////////////////////////////////////////////////////////


@app.route('/stock')
def stock():

    return render_template('stock.html')


@app.route('/agregar_stock', methods = ['POST'])
def add_stock():
    
    producto = Stock(fecha= datetime.datetime.now(),
                     producto = request.form['stock_producto'].upper(),
                     cantidad = request.form['stock_cantidad'],
                     accion = 'INGRESO', trabajo_id = 'NONE')
    
    db.session.add(producto)  
    db.session.commit()  

    last_row = db.session.query(Stock).order_by(Stock.id.desc()).first()

    flash('Producto agregado al stock satisfactoriamente')            
   
    return render_template('stock.html', producto = [last_row])



@app.route('/delete_stock')
def delete_stock(): 
    
    query = db.session.query(Stock).filter(Stock.trabajo_id == 'NONE').order_by(Stock.id.desc()).first()
    
    db.session.delete(query)
    db.session.commit()

    return redirect(url_for('stock'))


@app.route('/consulta_stock', methods = ['POST'])
def consulta_stock():
    if request.method == 'POST':

        ingreso = db.session.query(Stock.cantidad).filter(Stock.producto == request.form['consulta_producto'].upper()).filter(Stock.accion == 'INGRESO').all()
        egreso = db.session.query(Stock.cantidad).filter(Stock.producto == request.form['consulta_producto'].upper()).filter(Stock.accion == 'EGRESO').all()
        
        total = sum([x[0] for x in ingreso]) - sum([x[0] for x in egreso])
        

        return render_template('stock.html', item = request.form['consulta_producto'].upper(), x = '=', total = total)

if __name__ == '__main__':
    app.run(debug = True)