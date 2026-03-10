#Para el filtro de Roberts se necesita seguir los siguientes pasos:
#1. Convertir la imagen a escala de grises
#2. Aplicar la mascara de Roberts en ambas direcciones (Gx y Gy)
#3. Combinar los resultados de ambas mascaras para obtener la imagen final

from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import Tk

Tk().withdraw()
archivo = askopenfilename(title="Selecciona una imagen", filetypes=[("Archivos de imagen", "*.jpg;*.jpeg;*.png")])

imagen = Image.open(archivo)
pixeles = imagen.load()
ancho, alto = imagen.size

grises = Image.new("RGB", (ancho, alto), color="white")
pixeles_grises = grises.load()
for x in range(ancho):
    for y in range(alto):
        pixel = pixeles[x, y]
        r = pixel[0]
        g = pixel[1]
        b = pixel[2]
        a = (r+g+b) // 3        
        pixeles_grises[x, y] = (a, a, a)

roberts_gx = Image.new("RGB", (ancho, alto), color="white")
pixeles_gx = roberts_gx.load()
roberts_vertical = [[1, 0, 0],
                    [0, -1, 0],
                    [0, 0, 0]]
radio = len(roberts_vertical) // 2
for x in range(1, ancho-1):
    for y in range(1, alto-1):
        n = 0
        for j in range(-radio, radio+1):
            for i in range(-radio, radio+1):
                pixel = pixeles_grises[x+i, y+j]
                intensidad = pixel[0]
                n += intensidad * roberts_vertical[j+radio][i+radio]
        n = min(max(n, 0), 255)
        pixeles_gx[x, y] = (n, n, n)

roberts_gy = Image.new("RGB", (ancho, alto), color="white")
pixeles_gy = roberts_gy.load()
roberts_horizontal = [[0, 1, 0],
                      [-1, 0, 0],
                      [0, 0, 0]]
for x in range(1, ancho-1):
    for y in range(1, alto-1):
        n = 0
        for j in range(-radio, radio+1):
            for i in range(-radio, radio+1):
                pixel = pixeles_grises[x+i, y+j]
                intensidad = pixel[0]
                n += intensidad * roberts_horizontal[j+radio][i+radio]
        n = min(max(n, 0), 255)
        pixeles_gy[x, y] = (n, n, n)

filtro_roberts = Image.new("RGB", (ancho, alto), color="white")
pixeles_roberts = filtro_roberts.load()
for x in range(ancho):
    for y in range(alto):
        gx = pixeles_gx[x, y][0]
        gy = pixeles_gy[x, y][0]
        n = int((gx**2 + gy**2) ** 0.5)
        n = min(max(n, 0), 255)
        pixeles_roberts[x, y] = (n, n, n)

def guardar_imagen(event):
    Tk().withdraw()
    nombre_archivo = asksaveasfilename(
        title="Guardar imagen procesada",
        defaultextension=".png",
        filetypes=[("PNG", "*.png"),("JPEG", "*.jpg"),("BMP", "*.bmp")]
        )
    if nombre_archivo:
        filtro_roberts.save(nombre_archivo)
    else:
        print("Guardado cancelado")

fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(1, 5, figsize=(12, 8))

ax1.imshow(imagen)
ax1.axis("off")
ax1.set_title("Imagen Original")

ax2.imshow(grises)
ax2.axis("off")
ax2.set_title("Imagen en niveles de Gris")

ax3.imshow(roberts_gx)
ax3.axis("off")
ax3.set_title("Roberts Gx")

ax4.imshow(roberts_gy)
ax4.axis("off")
ax4.set_title("Roberts Gy")

ax5.imshow(filtro_roberts)
ax5.axis("off")
ax5.set_title("Filtro de Roberts")

plt.tight_layout()

plt.subplots_adjust(top=0.9)

ax_btn_guardar = plt.axes([0.48, 0.96, 0.1, 0.04])
btn_guardar = Button(ax_btn_guardar, 'Guardar',
                        color='lightcoral', hovercolor='salmon')
btn_guardar.on_clicked(guardar_imagen)

plt.show()