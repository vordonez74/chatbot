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

class MRP:
    def __init__(self):
        # Paso 1: Variables de entrada y salida
        self.stock_actual = ctrl.Antecedent(np.arange(0, 100, 1), 'stock_actual')
        self.lead_time = ctrl.Antecedent(np.arange(0, 100, 1), 'lead_time')
        self.consumo_promedio_diario = ctrl.Antecedent(np.arange(0, 50, 1), 'consumo_promedio_diario')
        self.cantidad_a_reponer = ctrl.Consequent(np.arange(0, 200, 1), 'cantidad_a_reponer')

        # Paso 2: Definir los conjuntos difusos para cada variable de entrada
        self.stock_actual['bajo'] = fuzz.trimf(self.stock_actual.universe, [0, 15, 30])
        self.stock_actual['medio'] = fuzz.trimf(self.stock_actual.universe, [16, 37, 60])
        self.stock_actual['alto'] = fuzz.trimf(self.stock_actual.universe, [38, 80, 100])

        self.lead_time['corto'] = fuzz.trimf(self.lead_time.universe, [0, 15, 30])
        self.lead_time['medio'] = fuzz.trimf(self.lead_time.universe, [16, 37, 60])
        self.lead_time['largo'] = fuzz.trimf(self.lead_time.universe, [38, 80, 100])

        self.consumo_promedio_diario['bajo'] = fuzz.trimf(self.consumo_promedio_diario.universe, [0, 12, 25])
        self.consumo_promedio_diario['medio'] = fuzz.trimf(self.consumo_promedio_diario.universe, [13, 26, 37])
        self.consumo_promedio_diario['alto'] = fuzz.trimf(self.consumo_promedio_diario.universe, [27, 38, 50])

        # Definir los conjuntos difusos para la variable de salida
        self.cantidad_a_reponer['bajo'] = fuzz.trimf(self.cantidad_a_reponer.universe, [0, 50, 100])
        self.cantidad_a_reponer['medio'] = fuzz.trimf(self.cantidad_a_reponer.universe, [51, 101, 150])
        self.cantidad_a_reponer['alto'] = fuzz.trimf(self.cantidad_a_reponer.universe, [102, 151, 200])

        # Paso 3: Definir las reglas difusas
        self.rules = [
            ctrl.Rule(self.stock_actual['bajo'] & self.lead_time['corto'] & self.consumo_promedio_diario['alto'], self.cantidad_a_reponer['medio']),
            ctrl.Rule(self.stock_actual['bajo'] & self.lead_time['corto'] & self.consumo_promedio_diario['alto'], self.cantidad_a_reponer['alto']),
            ctrl.Rule(self.stock_actual['bajo'] & self.lead_time['corto'] & self.consumo_promedio_diario['alto'], self.cantidad_a_reponer['alto']),

            ctrl.Rule(self.stock_actual['bajo'] & self.lead_time['medio'] & self.consumo_promedio_diario['bajo'], self.cantidad_a_reponer['alto']),
            ctrl.Rule(self.stock_actual['bajo'] & self.lead_time['medio'] & self.consumo_promedio_diario['medio'], self.cantidad_a_reponer['alto']),
            ctrl.Rule(self.stock_actual['bajo'] & self.lead_time['medio'] & self.consumo_promedio_diario['alto'], self.cantidad_a_reponer['alto']),

            ctrl.Rule(self.stock_actual['bajo'] & self.lead_time['largo'] & self.consumo_promedio_diario['bajo'], self.cantidad_a_reponer['medio']),
            ctrl.Rule(self.stock_actual['bajo'] & self.lead_time['largo'] & self.consumo_promedio_diario['medio'], self.cantidad_a_reponer['alto']),
            ctrl.Rule(self.stock_actual['bajo'] & self.lead_time['largo'] & self.consumo_promedio_diario['alto'], self.cantidad_a_reponer['alto']),

            ctrl.Rule(self.stock_actual['medio'] & self.lead_time['corto'] & self.consumo_promedio_diario['bajo'], self.cantidad_a_reponer['bajo']),
            ctrl.Rule(self.stock_actual['medio'] & self.lead_time['corto'] & self.consumo_promedio_diario['medio'], self.cantidad_a_reponer['medio']),
            ctrl.Rule(self.stock_actual['medio'] & self.lead_time['corto'] & self.consumo_promedio_diario['alto'], self.cantidad_a_reponer['alto']),

            ctrl.Rule(self.stock_actual['medio'] & self.lead_time['medio'] & self.consumo_promedio_diario['bajo'], self.cantidad_a_reponer['bajo']),
            ctrl.Rule(self.stock_actual['medio'] & self.lead_time['medio'] & self.consumo_promedio_diario['medio'], self.cantidad_a_reponer['medio']),
            ctrl.Rule(self.stock_actual['medio'] & self.lead_time['medio'] & self.consumo_promedio_diario['alto'], self.cantidad_a_reponer['alto']),

            ctrl.Rule(self.stock_actual['medio'] & self.lead_time['largo'] & self.consumo_promedio_diario['bajo'], self.cantidad_a_reponer['bajo']),
            ctrl.Rule(self.stock_actual['medio'] & self.lead_time['largo'] & self.consumo_promedio_diario['medio'], self.cantidad_a_reponer['medio']),
            ctrl.Rule(self.stock_actual['medio'] & self.lead_time['largo'] & self.consumo_promedio_diario['alto'], self.cantidad_a_reponer['alto']),

            ctrl.Rule(self.stock_actual['alto'] & self.lead_time['corto'] & self.consumo_promedio_diario['bajo'], self.cantidad_a_reponer['medio']),
            ctrl.Rule(self.stock_actual['alto'] & self.lead_time['corto'] & self.consumo_promedio_diario['medio'], self.cantidad_a_reponer['bajo']),
            ctrl.Rule(self.stock_actual['alto'] & self.lead_time['corto'] & self.consumo_promedio_diario['alto'], self.cantidad_a_reponer['bajo']),

            ctrl.Rule(self.stock_actual['alto'] & self.lead_time['medio'] & self.consumo_promedio_diario['bajo'], self.cantidad_a_reponer['medio']),
            ctrl.Rule(self.stock_actual['alto'] & self.lead_time['medio'] & self.consumo_promedio_diario['medio'], self.cantidad_a_reponer['bajo']),
            ctrl.Rule(self.stock_actual['alto'] & self.lead_time['medio'] & self.consumo_promedio_diario['alto'], self.cantidad_a_reponer['bajo']),

            ctrl.Rule(self.stock_actual['alto'] & self.lead_time['largo'] & self.consumo_promedio_diario['bajo'], self.cantidad_a_reponer['medio']),
            ctrl.Rule(self.stock_actual['alto'] & self.lead_time['largo'] & self.consumo_promedio_diario['medio'], self.cantidad_a_reponer['bajo']),
            ctrl.Rule(self.stock_actual['alto'] & self.lead_time['largo'] & self.consumo_promedio_diario['alto'], self.cantidad_a_reponer['bajo'])
        ]

        # Crear el controlador
        self.control = ctrl.ControlSystem(self.rules)

    def calcular_cantidad_a_reponer(self, stock_actual, lead_time, consumo_promedio_diario):
        # Paso 4: Evaluar el modelo con datos de entrada
        sistema_control = ctrl.ControlSystemSimulation(self.control)
        sistema_control.input['stock_actual'] = stock_actual
        sistema_control.input['lead_time'] = lead_time
        sistema_control.input['consumo_promedio_diario'] = consumo_promedio_diario
        sistema_control.compute()
        output = sistema_control.output['cantidad_a_reponer']
        return output


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
# Crear todas las tablas que aún no existen
#with app.app_context():
#        db.create_all()

@app.route('/', methods=['GET'])
def principal():
        return render_template('index.html')

@app.route('/webhook', methods=['GET'])
def test():
    return make_response(f"El stock actual es {inventario['1000158']['stock_actual']}",200)

@app.route('/webhook',methods=['POST'])
def dialogFlow():
    data = request.get_json()
    output = 0

    if data['queryResult']['intent']['displayName'] == 'Reponer':
        controller = MRP()
        material = data['queryResult']['parameters']['tipoMaterial'][0]
        print(f"el material recibido de dialogflow es {material}")
        if material in inventario:
            stock = inventario[material]['stock_actual']
            leadtime = inventario[material]['lead_time']
            consumo = inventario[material]['consumo_promedio_diario']

            output = controller.calcular_cantidad_a_reponer(stock, leadtime, consumo)
            resp = f"Se debe reponer la cantidad de {output}"

        else:
            resp = "El código del material no existe"
        responseData = {
            "fulfillmentText":resp
        }
    else:
        responseData = {
            "fulfillmentText":"Intem no implementada"
        }
        
    return jsonify(responseData)






if __name__=='__main__':
    app.run(debug=True) 
