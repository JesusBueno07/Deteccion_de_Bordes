from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import Tk

import math

archivo = None
imagen = ""
pixeles = ""
cambios = []
direcciones = []
primer_cambio = True
ancho, alto = 120, 100
imagen_original = "" #Crea una nueva imagen en blanco con el tamaño especificado
imagen_gaussiano = Image.new("RGB", (ancho, alto), color="white") #Crea una nueva imagen en blanco con el tamaño especificado
imagen_gradiente = Image.new("RGB", (ancho, alto), color="white") #Crea una nueva imagen en blanco con el tamaño especificado
imagen_magnitudDireccionGrad = Image.new("RGB", (ancho, alto), color="white") #Crea una nueva imagen en blanco con el tamaño especificado
imagen_supresion = Image.new("RGB", (ancho, alto), color="white") #Crea una nueva imagen en blanco con el tamaño especificado
imagen_hyteresis = Image.new("RGB", (ancho, alto), color="white") #Crea una nueva imagen en blanco con el tamaño especificado
imagen_procesada = Image.new("RGB", (ancho, alto), color="white") #Crea una nueva imagen en blanco con el mismo tamaño que la imagen original

def cargar_imagen(event):
    global imagen, pixeles, ancho, alto, imagen_original, imagen_escala_grises
    Tk().withdraw()
    archivo = askopenfilename(title="Seleccionar imagen", filetypes=[("Archivos de imagen", "*.jpg;*.jpeg;*.png;*.bmp")])
    if not archivo: exit()

    imagen = Image.open(archivo)
    ancho, alto = imagen.size
    imagen_escala_grises = Image.new("RGB", (ancho, alto), color="white") #Crea una nueva imagen en blanco con el tamaño especificado
    pixeles = imagen.load()

    aplicar_escalagrises()

def actualizar_visualizacion(titulo):
    global imagen, imagen_escala_grises, imagen_gaussiano, imagen_gradiente, imagen_supresion, imagen_procesada

    ax1.clear()
    ax1.imshow(imagen)
    ax1.set_title("1. Original")
    
    ax2.clear()
    ax2.imshow(imagen_escala_grises)
    ax2.set_title("2. Escala de Grises")

    ax3.clear()
    ax3.imshow(imagen_gaussiano)
    ax3.set_title("3. Suavizado Gaussiano")

    ax4.clear()
    ax4.imshow(imagen_gradiente)
    ax4.set_title("4. Gradiente (Sobel)")

    ax5.clear()
    ax5.imshow(imagen_supresion)
    ax5.set_title("5. Supresión de No Máximos")

    ax6.clear()
    ax6.imshow(imagen_procesada)
    ax6.set_title("6. Resultado Final (Histeresis)")

    fig.canvas.draw_idle()

def aplicar_escalagrises():
    global imagen_escala_grises
    pixeles_salida = imagen_escala_grises.load() #Crea un objeto PixelAccess para la imagen de gris

    for x in range(ancho):
        for y in range(alto):
                pixel = pixeles[x,y]
                r = pixel[0] #Valor de la dupla que retorna el pixel en la posición (x, y)
                g = pixel[1] #Con valores de tupla.
                b = pixel[2]
                g = (r+g+b) // 3 #Calcula el valor de gris como el promedio de los valores RGB

                div = 255 // 2 #Valor de división para determinar el rango del umbral

                pixeles_salida[x, y] = (g, g, g) #Asigna el valor de gris a los tres canales RGB
    actualizar_visualizacion("Escala de Grises") #Actualiza la vista de matplotlib
    aplicar_suavizadoGaussiano()

def aplicar_mascara(nombreMask, mask, imagen_destino):
    global imagen_escala_grises
    pixeles_entrada = imagen_escala_grises.load()
    pixeles_salida = imagen_destino.load() #Crea un objeto PixelAccess para la imagen de gris

    for x in range(ancho):
        for y in range(alto):
                n = r = g = b = 0
                radio = len(mask) // 2
                for dx in range(-radio, radio+1):
                     for dy in range(-radio, radio+1):
                            if 0 <= x+dx < ancho and 0 <= y+dy < alto: #Verifica que las coordenadas estén dentro de los límites de la imagen 
                                pixel = pixeles_entrada[x+dx,y+dy]
                                peso = mask[dx+radio][dy+radio]
                                r += pixel[0] * peso #Valor de la dupla que retorna el pixel en la posición (x, y)
                                g += pixel[1] * peso #Con valores de tupla.
                                b += pixel[2] * peso
                                n+=peso
                if n == 0: n = 1 #Evita división por cero
                r, g, b = r//n, g//n, b//n #Calcula el valor de gris como el promedio de los valores RGB
                pixeles_salida[x, y] = (r, g, b) #Asigna el valor de gris a los tres canales RGB
    actualizar_visualizacion(f"{nombreMask} {len(mask)}x{len(mask)}" if nombreMask == "Suavizado" else f"{nombreMask}") #Actualiza la vista de matplotlib

def aplicar_suavizadoGaussiano():
    global imagen_gaussiano

    mask = [
        [1,2,1],
        [2,4,2],
        [1,2,1]
    ]

    imagen_gaussiano = Image.new("RGB", (ancho, alto), color="white") #Crea una nueva imagen en blanco con el tamaño especificado
    aplicar_mascara("Suavizado Gaussiano", mask, imagen_gaussiano)
    obtener_gradiente()

def obtener_gradiente():
    global imagen_gradiente, imagen_gaussiano, direcciones
    imagen_gradiente = Image.new("RGB", (ancho, alto), color="white") #Crea una nueva imagen en blanco con el tamaño especificado

    pixeles_entrada = imagen_gaussiano.load()
    pixeles_salida = imagen_gradiente.load() #Crea un objeto PixelAccess para la imagen de gris

    direcciones = [[0]*alto for _ in range(ancho)] #Obtiene la direcciones de los gradientes para cada pixel

    mask_x = [
        [-1,0,1],
        [-2,0,2],
        [-1,0,1]
    ]

    mask_y = [
        [1,2,1],
        [0,0,0],
        [-1,-2,-1]
    ]

    for x in range(ancho):
         for y in range(alto):
                gx = gy = 0
                radio = len(mask_x) // 2
                for dx in range(-radio, radio+1):
                    for dy in range(-radio, radio+1):
                        if 0 <= x+dx < ancho and 0 <= y+dy < alto:
                            pixel = pixeles_entrada[x+dx, y+dy][0]

                            peso_x = mask_x[dy+radio][dx+radio]
                            peso_y = mask_y[dy+radio][dx+radio]

                            gx += pixel * peso_x
                            gy += pixel * peso_y
                magnitud = int((gx**2 + gy**2)**0.5)

                direccion = math.degrees(math.atan2(gy, gx))
                if direccion < 0:
                    direccion += 180
                
                direcciones[x][y] = direccion

                # direccion = int((180 / 3.14159) * atan2(gy, gx)) % 180
                magnitud = int(max(0, min(255, magnitud)))
                pixeles_salida[x, y] = (magnitud, magnitud, magnitud)
    actualizar_visualizacion("Gradiente") #Actualiza la vista de matplotlib
    aplicar_supresionMax()

def aplicar_supresionMax():
    global imagen_supresion, imagen_gradiente, direcciones

    imagen_supresion = Image.new("RGB", (ancho, alto), color="white")

    pixeles_entrada = imagen_gradiente.load()
    pixeles_salida = imagen_supresion.load()

    for x in range(1, ancho-1):
        for y in range(1, alto-1):

            magnitud = pixeles_entrada[x, y][0]
            direccion = direcciones[x][y]

            if (0 <= direccion < 22.5) or (157.5 <= direccion <= 180):
                vecino1 = pixeles_entrada[x-1, y][0]
                vecino2 = pixeles_entrada[x+1, y][0]

            elif 22.5 <= direccion < 67.5:
                vecino1 = pixeles_entrada[x-1, y-1][0]
                vecino2 = pixeles_entrada[x+1, y+1][0]

            elif 67.5 <= direccion < 112.5:
                vecino1 = pixeles_entrada[x, y-1][0]
                vecino2 = pixeles_entrada[x, y+1][0]

            else:
                vecino1 = pixeles_entrada[x-1, y+1][0]
                vecino2 = pixeles_entrada[x+1, y-1][0]

            if magnitud >= vecino1 and magnitud >= vecino2:
                pixeles_salida[x, y] = (magnitud, magnitud, magnitud)
            else:
                pixeles_salida[x, y] = (0, 0, 0)
    actualizar_visualizacion("Supresión de No Máximos") #Actualiza la vista de matplotlib
    aplicar_umbral_doble()

def aplicar_umbral_doble(): #Clasificamos los pixeles en 3 tipos: bordes fuertes, bordes débiles y no bordes, dependiendo de su magnitud en comparación con dos umbrales predefinidos.
    # magnitud >= umbral_alto = borde fuerte
    # magnitud >= umbral_bajo = borde débil
    # magnitud < umbral_bajo = no borde

    global imagen_umbral, imagen_supresion

    imagen_umbral = Image.new("RGB", (ancho, alto), color="black")

    pixeles_entrada = imagen_supresion.load()
    pixeles_salida = imagen_umbral.load()

    umbral_alto = 100
    umbral_bajo = 50

    for x in range(ancho):
        for y in range(alto):

            magnitud = pixeles_entrada[x,y][0]

            if magnitud >= umbral_alto:
                pixeles_salida[x,y] = (255,255,255)  #borde fuerte

            elif magnitud >= umbral_bajo:
                pixeles_salida[x,y] = (100,100,100)  #borde débil

            else:
                pixeles_salida[x,y] = (0,0,0)  #no borde
    actualizar_visualizacion("Umbral Doble") #Actualiza la vista de matplotlib
    aplicar_histeresis()

def aplicar_histeresis():
    global imagen_procesada, imagen_umbral
    imagen_procesada = Image.new("RGB", (ancho, alto), color="black")

    pixeles_entrada = imagen_umbral.load()
    pixeles_salida = imagen_procesada.load()

    for x in range(1, ancho-1):
        for y in range(1, alto-1):
            pixel = pixeles_entrada[x,y][0]
            if pixel == 255:
                pixeles_salida[x,y] = (255,255,255)
            elif pixel == 100:
                conectado = False
                for dx in [-1,0,1]:
                    for dy in [-1,0,1]:
                        vecino = pixeles_entrada[x+dx, y+dy][0]
                        if vecino == 255:
                            conectado = True
                if conectado:
                    pixeles_salida[x,y] = (255,255,255)
                else:
                    pixeles_salida[x,y] = (0,0,0)
            else:
                pixeles_salida[x,y] = (0,0,0)
    actualizar_visualizacion("Histeresis") #Actualiza la vista de matplotlib

fig, ((ax1, ax2, ax3),
      (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(10, 5))
plt.tight_layout(pad=4) #Ajusta el diseño de la figura para evitar solapamientos

#BOTONES
axn_btn_abrirImg = plt.axes([0.01, 0.91, 0.12, 0.06])
btn_abrirImg = Button(axn_btn_abrirImg, 'Abrir Imagen', color='lightcyan', hovercolor='cyan')

btn_abrirImg.on_clicked(cargar_imagen)

plt.show()