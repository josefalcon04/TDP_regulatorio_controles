import os, logging
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Usa un backend sin interfaz gráfica
import matplotlib.pyplot as plt
import io
import base64
import pyodbc
from flask import Flask, render_template, request, send_file, Blueprint
from flask import send_from_directory
from sqlalchemy import create_engine
import numpy as np

# Variable global para almacenar el valor máximo de CANTIDAD
max_y_global = 0

def ConnectTD():
    try:
        engine = create_engine("teradatasql://ic_jfalconf:OQ38b&655@teraprod.gp.inet")        
        return engine
    except Exception as e:
        logging.error(f"Error de conexión a Teradata: {e}")
        return None
    
def Query_Teradata():
    print("Query_Teradata")    
    engine = ConnectTD()
    
    if not engine:
        logging.error("No se pudo conectar a Teradata")
        return []

    sql_trd = """
    --select PERIODO, 
    --CASE 
    --WHEN D_ESTADO IN ('PROD COMERCIAL ACTIVO') THEN 'ACTIVO' 
    --WHEN D_ESTADO IN ('PRODUCTO COMERCIAL SUSPENDIDO') THEN 'SUSPENDIDO'
    --else D_ESTADO
    --END AS D_ESTADO,
    --CASE 
    --WHEN INT_TECNOLOGIA IN ('FTTH', 'ADSL', 'HFC') THEN INT_TECNOLOGIA 
    --WHEN INT_TECNOLOGIA IN ('VDSL', 'COPPER') THEN 'ADSL'
    --END AS BA_TECNOLOGIA,
    --count(*) as CANTIDAD
    --from DBI_PUBLIC.JRR_BA_PLANTA
    --WHERE PERIODO >= 202401
    --group by 1,2,3
    --order by 1,2,3 asc;
    select * from PE_DESA_REG_DATA.TMP_REG_BA_PLANTA
    ORDER BY 1 desc , 2 asc ;
    """

    try:
        df_trd = pd.read_sql(sql_trd, engine)
        print("Query terada OK")
        return df_trd.to_dict(orient="records")
        
    except Exception as ERR_TERA:
        logging.error(f"Error al ejecutar la consulta en Query_Teradata: {ERR_TERA}")
        return []
    finally:
        engine.dispose()
        print("Conexión a Teradata cerrada")

def Query_Teradata2():
    print("Query_Teradata2")    
    engine = ConnectTD()
    
    if not engine:
        logging.error("No se pudo conectar a Teradata")
        return []

    sql_trd2 = """
    --select TO_CHAR(PERIODO,'YYYYMM') AS PERIODO,
    --CASE 
    --WHEN D_ESTADO IN ('ACTIVO', 'PROD COMERCIAL ACTIVO') THEN 'ACTIVO' 
    --WHEN D_ESTADO IN ('SUSPENDIDO', 'PRODUCTO COMERCIAL SUSPENDIDO') THEN 'SUSPENDIDO'
    --else D_ESTADO
    --END AS D_ESTADO,
    --BA_tecnologia,count(*) as CANTIDAD
    --from PE_PROD_INH_DATA.T_INH_PLT_CHURN_FIJA 
    --where PERIODO >= date '2024-01-01'
    --and BA_TECNOLOGIA is not null
    --and BA_tecnologia not in ('COPP')
    --and D_ESTADO is not null
    --group by 1,2,3
    --order by 1,2,3 asc;
    select * from PE_DESA_REG_DATA.TMP_REG_BA_CONTROL
    ORDER BY 1 desc , 2 asc ;
    """

    try:
        df_trd2 = pd.read_sql(sql_trd2, engine)
        print("Query terada2 OK")
        return df_trd2.to_dict(orient="records")
        
    except Exception as ERR_TERA:
        logging.error(f"Error al ejecutar la consulta en Query_Teradata2: {ERR_TERA}")
        return []
    finally:
        engine.dispose()
        print("Conexión a Teradata2 cerrada")

# Colores fijos asignados por tecnología
COLORES_TECNOLOGIA = {
    "ADSL": "#ff7f0e",  # Naranja
    "FTTH": "#1f77b4",  # Celeste
    "HFC": "#2ca02c"    # Verde
}


planta_control_bp = Blueprint('planta', __name__, url_prefix='/planta')

app = Flask(__name__, template_folder="Menu/templates") 

@planta_control_bp.route('/')
def index():
    print("index")
    # Ejecutar las consultas en Teradata
    df1 = Query_Teradata()
    df2 = Query_Teradata2()

    if not df1 or not df2:
        return "<h2>Error al obtener datos de Teradata</h2>", 503

    df1 = pd.DataFrame(df1)
    df2 = pd.DataFrame(df2)
    
    # Obtener las tecnologías y agregar la opción "Todas"
    tecnologias1 = df1["BA_TECNOLOGIA"].unique().tolist()    
    tecnologias1.insert(0, "TODAS")

    tecnologias2 = df2["BA_TECNOLOGIA"].unique().tolist()    
    tecnologias2.insert(0, "TODAS")

    # Obtener los estados únicos por cada consulta
    estados1 = df1["D_ESTADO"].unique().tolist()
    estados2 = df2["D_ESTADO"].unique().tolist()
    
    # Obtener los periodos
    periodo1 = df1["PERIODO"].unique().tolist()
    periodo2 = df2["PERIODO"].unique().tolist()

    print("Fin-index")    
    return render_template('planta.html', 
                            tecnologias1=tecnologias1,
                            tecnologias2=tecnologias2, 
                            estados1=estados1,
                            estados2=estados2,
                            periodo1=periodo1,
                            periodo2=periodo2)
    

def generar_grafico(df, img_name):
    global max_y_global

    # Verificar que las columnas necesarias existen
    required_columns = {"D_ESTADO", "BA_TECNOLOGIA", "PERIODO", "CANTIDAD"}
    if not required_columns.issubset(df.columns):
        return "Error: Los datos no contienen las columnas necesarias", 500

    # Obtener parámetros de la URL
    tecnologia = request.args.get("tecnologia", "TODAS")
    estado = request.args.get("estado", "PROD COMERCIAL ACTIVO")
    periodos = request.args.get("periodo", "").split(",") if request.args.get("periodo") else []

    print("Tecnología:", tecnologia)
    print("Estado:", estado)
    print("Periodos recibidos:", periodos)

    # Filtrar datos por estado seleccionado
    df = df[df["D_ESTADO"] == estado]

    # Convertir PERIODO a string y ordenar
    df["PERIODO"] = df["PERIODO"].astype(str)
    df = df.sort_values("PERIODO")

    if periodos:
        df = df[df["PERIODO"].isin(periodos)]
    
    if df.empty:
        return "No hay datos disponibles para la selección", 404

    # Si no se ha calculado `max_y_global`, hacerlo ahora
    if max_y_global == 0:
        max_y_global = df["CANTIDAD"].max()

    # Ajustar tamaño del gráfico
    plt.figure(figsize=(14, 5))

    tecnologias_unicas = df["BA_TECNOLOGIA"].unique()

    if tecnologia == "TODAS":
        for tech in tecnologias_unicas:
            df_tech = df[df["BA_TECNOLOGIA"] == tech]
            color = COLORES_TECNOLOGIA.get(tech, "#000000")  # Color negro si no hay color asignado
            plt.plot(df_tech["PERIODO"], df_tech["CANTIDAD"], marker="o", linestyle="-", label=tech, color=color)
    else:
        df = df[df["BA_TECNOLOGIA"] == tecnologia]
        if df.empty:
            return "No hay datos disponibles para la selección", 404
        color = COLORES_TECNOLOGIA.get(tecnologia, "#000000")
        plt.plot(df["PERIODO"], df["CANTIDAD"], marker="o", linestyle="-", label=tecnologia, color=color)

    plt.xlabel("Período")
    plt.ylabel("Cantidad")
    if not df["PERIODO"].empty:
        plt.xticks(df["PERIODO"].unique(), rotation=0)
    
    plt.ylim(0, max_y_global * 1.1)
    plt.grid(True)
    plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.2), ncol=len(tecnologias_unicas))

    # Guardar la imagen en el directorio estático
    ruta_imagen = os.path.join(os.getcwd(), "menu", "static", "img", img_name)
    print(f"Ruta de guardado: {ruta_imagen}")
    plt.savefig(ruta_imagen)
    plt.close()
    
    print("Directorio actual:", os.getcwd())
    
    return send_file(ruta_imagen, mimetype='image/png')

@app.route('/grafico1')
def create_plot1():
    print("create_plot1")
    df1 = Query_Teradata()
    print(df1)
    if not df1:
        return "Error al obtener datos de Teradata", 500
    df1 = pd.DataFrame(df1)
    return generar_grafico(df1, "grafico1.png")

@app.route('/grafico2')
def create_plot2():
    print("create_plot2")
    df2 = Query_Teradata2()
    print(df2)
    if not df2:
        return "Error al obtener datos de Teradata", 500
    df2 = pd.DataFrame(df2)
    return generar_grafico(df2, "grafico2.png")

if __name__ == '__main__':
    app.run(debug=True)
