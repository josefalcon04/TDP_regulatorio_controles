from flask import Flask, render_template, request, Response, jsonify
import numpy as np
import matplotlib.pyplot as plt
import io
import random
import tensorflow as tf
from tensorflow import keras
import pandas as pd

app = Flask(__name__)

# Datos simulados
tecnologias1 = ["5G", "4G", "Fibra"]
estados1 = ["Activo", "Inactivo"]
periodo1 = ["202401", "202402", "202403"]

# Función para entrenar y predecir
def entrenar_y_predecir(periodos):
    datos = np.array([random.randint(50, 200) for _ in range(len(periodos))])  # Valores aleatorios
    df = pd.DataFrame({"Periodo": list(map(int, periodos)), "Valor": datos})

    X = df["Periodo"].values.reshape(-1, 1)
    y = df["Valor"].values.reshape(-1, 1)

    X_min, X_max = X.min(), X.max()
    X_norm = (X - X_min) / (X_max - X_min)

    modelo = keras.Sequential([
        keras.layers.Dense(10, activation="relu", input_shape=(1,)),
        keras.layers.Dense(10, activation="relu"),
        keras.layers.Dense(1)
    ])
    modelo.compile(optimizer="adam", loss="mse")
    modelo.fit(X_norm, y, epochs=100, verbose=0)

    proximo_periodo = np.array([[int(periodos[-1]) + 1]])  # Predicción del siguiente período
    proximo_periodo_norm = (proximo_periodo - X_min) / (X_max - X_min)
    prediccion = modelo.predict(proximo_periodo_norm)[0][0]

    return df, proximo_periodo[0][0], prediccion

# Nueva ruta para obtener la predicción en texto
@app.route("/prediccion_texto")
def prediccion_texto():
    tecnologia = request.args.get("tecnologia", "5G")
    estado = request.args.get("estado", "Activo")
    periodos = request.args.get("periodo", "").split(",")

    if not periodos or periodos == [""]:
        periodos = periodo1  # Usar todos los períodos si no se especifican

    df, proximo_periodo, prediccion = entrenar_y_predecir(periodos)

    # Análisis del crecimiento
    diferencia = prediccion - df["Valor"].iloc[-1]
    tendencia = "aumentando" if diferencia > 0 else "disminuyendo"
    porcentaje = abs(diferencia / df["Valor"].iloc[-1]) * 100

    resumen = f"Para {tecnologia} en estado {estado}, se predice un valor de {int(prediccion)} para el período {proximo_periodo}. " \
              f"Esto representa un cambio de {int(diferencia)} ({porcentaje:.2f}%) respecto al último dato, mostrando una tendencia {tendencia}."

    return jsonify({"resumen": resumen})

# Ruta del gráfico
@app.route("/grafico1")
def grafico1():
    tecnologia = request.args.get("tecnologia", "5G")
    estado = request.args.get("estado", "Activo")
    periodos = request.args.get("periodo", "").split(",")

    if not periodos or periodos == [""]:
        periodos = periodo1  # Usar todos los períodos si no se especifican

    df, proximo_periodo, prediccion = entrenar_y_predecir(periodos)

    plt.figure(figsize=(6, 4))
    plt.plot(df["Periodo"], df["Valor"], marker="o", label="Datos Reales")
    plt.scatter(proximo_periodo, prediccion, color="red", label=f"Predicción {proximo_periodo}: {int(prediccion)}")
    plt.xlabel("Período")
    plt.ylabel("Valor")
    plt.title(f"Gráfico de {tecnologia} - {estado}")
    plt.legend()
    plt.grid()

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close()

    return Response(img.getvalue(), mimetype="image/png")

@app.route("/")
def index():
    return render_template("planta2.html", tecnologias1=tecnologias1, estados1=estados1, periodo1=periodo1)

# Iniciar la aplicación
if __name__ == "__main__":
    app.run(debug=True)
