from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql1234",
    database="cashback_db"
)

def calcular_cashback(valor_compra, desconto_percentual, tipo_cliente):
    valor_final = valor_compra * (1 - desconto_percentual / 100)
    cashback_base = valor_final * 0.05

    if tipo_cliente.lower() == "vip":
        cashback = cashback_base + (cashback_base * 0.10)
    else:
        cashback = cashback_base

    if valor_final > 500:
        cashback *= 2

    return round(cashback, 2)

@app.route("/calcular", methods=["POST"])
def calcular():
    data = request.json
    valor = float(data["valor"])
    desconto = float(data["desconto"])
    tipo = data["tipo"]
    ip = request.remote_addr

    cashback = calcular_cashback(valor, desconto, tipo)

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO consultas (ip, tipo, valor, cashback) VALUES (%s, %s, %s, %s)",
        (ip, tipo, valor, cashback)
    )
    conn.commit()

    return jsonify({"cashback": cashback})

@app.route("/historico", methods=["GET"])
def historico():
    ip = request.remote_addr
    cursor = conn.cursor()
    cursor.execute("SELECT tipo, valor, cashback FROM consultas WHERE ip = %s", (ip,))
    dados = cursor.fetchall()

    return jsonify(dados)

app.run(debug=True)