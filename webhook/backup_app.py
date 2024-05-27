from flask import Flask, request, jsonify, make_response, render_template
from flask_sqlalchemy import SQLAlchemy 
from os import environ
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__='users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    #def __init__(self, username, email):
    #    self.username = username
    #    self.email = email

    def json(self):
        return {'id': id,'username': self.username, 'email': self.email}

# Crear todas las tablas que aún no existen
with app.app_context():
        db.create_all()

@app.route('/', methods=['GET'])
def principal():
        return render_template('index.html')

@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message':'test route'}),200)

# create a user
@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = requests.get_json()
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
