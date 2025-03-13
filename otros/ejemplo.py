import matplotlib.pyplot as plt

# Crear algunos datos para graficar
x = [1, 2, 3, 4, 5]
y = [1, 4, 9, 16, 25]

# Crear el gráfico
plt.plot(x, y)

# Guardar la figura como una imagen
plt.savefig('grafico.png')  # Guarda la imagen en el directorio actual
plt.close()  # Cierra la figura para evitar mostrarla en el script
