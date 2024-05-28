from flask import Flask, request, jsonify, make_response, render_template
from flask_sqlalchemy import SQLAlchemy 
from os import environ
from config import Config
from skfuzzy import control as ctrl
import numpy as np
import skfuzzy as fuzz



app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
inventario = {
    "1000889": {
        "material": "1000889",
        "stock_actual": 30,
        "lead_time": 10,
        "consumo_promedio_diario": 20
    },
    "1000010": {
        "material": "1000010",
        "stock_actual": 5,
        "lead_time": 15,
        "consumo_promedio_diario": 38
    },
    "1000011": {
        "material": "1000011",
        "stock_actual": 80,
        "lead_time": 60,
        "consumo_promedio_diario": 12
    },
    "1000158": {
        "material": "1000158",
        "stock_actual": 30,
        "lead_time": 60,
        "consumo_promedio_diario": 26
}
                        }
class User(db.Model):
    __tablename__='users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def json(self):
        return {'id': id,'username': self.username, 'email': self.email}

# Crear todas las tablas que aún no existen
with app.app_context():
        db.create_all()

@app.route('/', methods=['GET'])
def principal():
        return render_template('index.html')

@app.route('/webhook', methods=['GET'])
def test():
    return make_response(f"El stock actual es {inventario['1000158']['stock_actual']}",200)

@app.route('/webhook',methods=['POST'])
def dialogFlow():
    data = request.get_json()
    valor = 0
    if data['queryResult']['intent']['displayName'] == 'Reponer':
        material = data['queryResult']['parameters']['tipoMaterial']
        valor = 10
        responseData = {
            "fulfillmentText":f"Se debe reponer la cantidad de {valor}"
            }
    return jsonify(responseData)










# create a user
@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        new_user = User(username=data['username'], email=data['email'])
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({'message':'user created'}), 201)
    except e:
        return make_response(jsonify({'message':'error creating user'}), 500)

# get all users
@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        if len(users):
            return make_response(jsonify({'users':[user.json() for user in users]}), 200)
        return make_response(jsonify({'message': 'no users found'}), 404)
    except e:
        return make_response(jsonify({'message': 'error getting users'}), 500)


# get a user by id
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            return make_response(jsonify({'user':user.json()}),200)
        return make_response(jsonify({'message':'user not found'}), 404)
    except e:
        return make_response(jsonify({'message':'error getting user'}), 500)


# update a user
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            data = request.get_json()
            user.username = data['username']
            user.email = data['email']
            db.session.commit()
            return make_response(jsonify({ 'message': 'user updated'}), 200)
        return make_response(jsonify({'message':'user not found'}), 404)
    except e:
        return make_response(jsonify({'messag': 'error updating user'}), 500)


# delete a user
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return make_response(jsonify({'message': 'user deleted'}), 200)
        return make_response(jsonify({ 'message': 'user not found'}), 404)
    except e:
        return make_response(jsonify({ 'message': 'error deleting user'}), 500)

if __name__=='__main__':
    app.run(debug=True) 
