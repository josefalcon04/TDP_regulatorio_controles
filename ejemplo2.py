import pyodbc
import matplotlib.pyplot as plt

# Establecer la conexión con la base de datos Netezza
conn = pyodbc.connect('DRIVER={NetezzaSQL};'
                      'SERVER=10.4.35.1;'
                      'PORT=5480;'  # Puerto por defecto de Netezza
                      'DATABASE=SB_BI;'
                      'UID=jfalconf;'
                      'PWD=jfalconf23!')

# Crear un cursor para ejecutar la consulta
cursor = conn.cursor()

# Ejecutar una consulta SELECT con múltiples columnas como eje Y
cursor.execute('SELECT tipo, "1", "2", "3" FROM CONTROL_MAKO..T_TENDENCIA_NORMA;')

# Obtener los resultados
resultados = cursor.fetchall()

# Separar los resultados en listas
x = [fila[0] for fila in resultados]  # 'tipo' (Eje X)
y1 = [fila[1] for fila in resultados]  # '1' (Eje Y)
y2 = [fila[2] for fila in resultados]  # '2' (Eje Y)
y3 = [fila[3] for fila in resultados]  # '3' (Eje Y)

# Crear el gráfico
plt.figure(figsize=(10, 5))
plt.plot(x, y1, marker='o', linestyle='-', label='Valor de "1"')  
plt.plot(x, y2, marker='s', linestyle='--', label='Valor de "2"')  
plt.plot(x, y3, marker='^', linestyle='-.', label='Valor de "3"')  

# Mostrar valores en cada punto
for i in range(len(x)):
    plt.text(x[i], y1[i], f'{y1[i]}', fontsize=9, ha='center', va='bottom')
    plt.text(x[i], y2[i], f'{y2[i]}', fontsize=9, ha='center', va='bottom')
    plt.text(x[i], y3[i], f'{y3[i]}', fontsize=9, ha='center', va='bottom')

# Etiquetas de los ejes
plt.xlabel('Eje X (tipo)')
plt.ylabel('Valores en Y')

# Título del gráfico
plt.title('Gráfico de Netezza con múltiples valores en Y')

# Mostrar la leyenda
plt.legend()

# Mostrar la cuadrícula
plt.grid()

plt.savefig('grafico2.png')  # Guarda la imagen en el directorio actual

# Mostrar el gráfico
plt.show()

# Cerrar la conexión
cursor.close()
conn.close()
