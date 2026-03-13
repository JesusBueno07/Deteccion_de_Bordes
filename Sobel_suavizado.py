#Para el algoritmo de Sobel se necesita seguir los siguientes pasos:
#1. Convertir la imagen a escala de grises
#2. Aplicar la mascara de Sobel en ambas direcciones (Gx y Gy)
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

suavizado = Image.new("RGB", (ancho, alto), color="white")
pixeles_suavizado = suavizado.load()
suavizado = [[1/9, 1/9, 1/9],
             [1/9, 1/9, 1/9],
             [1/9, 1/9, 1/9]]
radio = len(suavizado) // 2
for x in range(1, ancho-1):
    for y in range(1, alto-1):
        r = g = b = 0
        for j in range(-radio, radio+1):
            for i in range(-radio, radio+1):
                pixel = pixeles[x+i, y+j]
                r += pixel[0] * suavizado[j+radio][i+radio]
                g += pixel[1] * suavizado[j+radio][i+radio]
                b += pixel[2] * suavizado[j+radio][i+radio]
        r = min(max(int(r), 0), 255)
        g = min(max(int(g), 0), 255)
        b = min(max(int(b), 0), 255)
        pixeles_suavizado[x, y] = (r, g, b)

grises = Image.new("RGB", (ancho, alto), color="white")
pixeles_grises = grises.load()
for x in range(ancho):
    for y in range(alto):
        pixel = pixeles_suavizado[x, y]
        r = pixel[0]
        g = pixel[1]
        b = pixel[2]
        a = (r+g+b) // 3        
        pixeles_grises[x, y] = (a, a, a)

sobel_gx = Image.new("RGB", (ancho, alto), color="white")
pixeles_gx = sobel_gx.load()
sobel_horizontal = [[-1, 0, 1],
                    [-2, 0, 2], 
                    [-1, 0, 1]]
radio = len(sobel_horizontal) // 2
for x in range(1, ancho-1):
    for y in range(1, alto-1):
        n = 0        
        for j in range(-radio, radio+1):
            for i in range(-radio, radio+1):
                pixel = pixeles_grises[x+i, y+j]
                intensidad = pixel[0]
                n += intensidad * sobel_horizontal[j+radio][i+radio]
        n = min(max(n, 0), 255)
        pixeles_gx[x, y] = (n, n, n)

sobel_gy = Image.new("RGB", (ancho, alto), color="white")
pixeles_gy = sobel_gy.load()
sobel_vertical = [[-1, -2, -1],
                  [0, 0, 0],
                  [1, 2, 1]]
for x in range(1, ancho-1):
    for y in range(1, alto-1):
        n = 0        
        for j in range(-radio, radio+1):
            for i in range(-radio, radio+1):
                pixel = pixeles_grises[x+i, y+j]
                intensidad = pixel[0]
                n += intensidad * sobel_vertical[j+radio][i+radio]
        n = min(max(n, 0), 255)
        pixeles_gy[x, y] = (n, n, n)

filtro_sobel = Image.new("RGB", (ancho, alto), color="white")
pixeles_sobel = filtro_sobel.load()
for x in range(ancho):
    for y in range(alto):
        gx = pixeles_gx[x, y][0]
        gy = pixeles_gy[x, y][0]
        n = int((gx**2 + gy**2) ** 0.5)
        n = min(max(n, 0), 255)
        pixeles_sobel[x, y] = (n, n, n)

filtro_gaussiano = Image.new("RGB", (ancho, alto), color="white")
pixeles_gaussiano = filtro_gaussiano.load()
gaussiano = [[1, 4, 7, 4, 1],
            [4, 16, 26, 16, 4],
            [7, 26, 41, 26, 7],
            [4, 16, 26, 16, 4],
            [1, 4, 7, 4, 1]]
radio_gaus = len(gaussiano) // 2
for x in range(2, ancho-2):
    for y in range(2, alto-2):
        n = r = g = b = 0
        for j in range(-radio_gaus, radio_gaus+1):
            for i in range(-radio_gaus, radio_gaus+1):
                pixel = pixeles_grises[x+i, y+j]
                peso = gaussiano[j+radio_gaus][i+radio_gaus]
                r += pixel[0] * peso
                g += pixel[1] * peso
                b += pixel[2] * peso
                n += peso
        r, g ,b = r//n, g//n, b//n
        pixeles_gaussiano[x, y] = (r, g, b)

filtro_laplaciano = Image.new("RGB", (ancho, alto), color="white")
pixeles_laplaciano = filtro_laplaciano.load()
laplaciano = [[0, 1, 0],
              [1, -4, 1],
              [0, 1, 0]]
for x in range(1, ancho-1):
    for y in range(1, alto-1):
        n = 0        
        for j in range(-radio, radio+1):
            for i in range(-radio, radio+1):
                pixel = pixeles_gaussiano[x+i, y+j]
                intensidad = pixel[0]
                n += intensidad * laplaciano[j+radio][i+radio]
        n = min(max(n, 0), 255)
        pixeles_laplaciano[x, y] = (n, n, n)

def guardar_imagen(event):
    Tk().withdraw()
    nombre_archivo = asksaveasfilename(
        title="Guardar imagen procesada",
        defaultextension=".png",
        filetypes=[("PNG", "*.png"),("JPEG", "*.jpg"),("BMP", "*.bmp")]
        )
    if nombre_archivo:
        filtro_laplaciano.save(nombre_archivo)
    else:
        print("Guardado cancelado")

def guardar_imagen1(event):
    Tk().withdraw()
    nombre_archivo = asksaveasfilename(
        title="Guardar imagen procesada",
        defaultextension=".png",
        filetypes=[("PNG", "*.png"),("JPEG", "*.jpg"),("BMP", "*.bmp")]
        )
    if nombre_archivo:
        filtro_sobel.save(nombre_archivo)
    else:
        print("Guardado cancelado")

fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(1, 6, figsize=(14, 8))

ax1.imshow(imagen)
ax1.axis("off")
ax1.set_title("Imagen Original")

ax2.imshow(grises)
ax2.axis("off")
ax2.set_title("Imagen en Escala de Grises")

ax3.imshow(sobel_gx)
ax3.axis("off")
ax3.set_title("Sobel Gx")

ax4.imshow(sobel_gy)
ax4.axis("off")
ax4.set_title("Sobel Gy")

ax5.imshow(filtro_sobel)
ax5.axis("off")
ax5.set_title("Filtro Sobel")

ax6.imshow(filtro_laplaciano)
ax6.axis("off")
ax6.set_title("Filtro Laplaciano")

plt.tight_layout()

plt.subplots_adjust(top=0.9)

ax_btn_guardar = plt.axes([0.9, 0.96, 0.08, 0.04])
btn_guardar = Button(ax_btn_guardar, 'Guardar filtro Laplaciano',
                    color='lightcoral', hovercolor='salmon')
btn_guardar.on_clicked(guardar_imagen)

ax_btn_guardar1 = plt.axes([0.48, 0.96, 0.1, 0.04])
btn_guardar1 = Button(ax_btn_guardar1, 'Guardar filtro Sobel',
                    color='lightcoral', hovercolor='salmon')
btn_guardar1.on_clicked(guardar_imagen1)

plt.show()