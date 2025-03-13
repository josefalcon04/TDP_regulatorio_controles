from flask import Flask, render_template
from calendario import calendario_bp  # Importamos el blueprint del calendario
from monitoreo_reporte import monitoreo_bp  # Importamos el blueprint de monitoreo
from planta import planta_control_bp # Importamos el blueprint de planta de control

app = Flask(__name__)
app.register_blueprint(calendario_bp)  # Registramos el calendario en Flask
app.register_blueprint(monitoreo_bp)
app.register_blueprint(planta_control_bp)

@app.route('/')
def menu():
    return render_template('menu.html')  # Muestra el menú con la barra lateral

if __name__ == '__main__':
    app.run(debug=True)
