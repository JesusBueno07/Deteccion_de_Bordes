from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, CheckButtons, RadioButtons
from tkinter.filedialog import askopenfilename
from tkinter import Tk
import math

# --- Variables Globales ---
imagen_original = None
ancho, alto = 0, 0
usar_suavizado = False
usar_saturacion = False
usar_laplaciano = False
metodo_bordes = 'Sobel'

def cargar_imagen(event):
    global imagen_original, ancho, alto
    Tk().withdraw()
    archivo = askopenfilename(title="Selecciona una imagen", filetypes=[("Imagen", "*.jpg;*.jpeg;*.png")])
    if archivo:
        imagen_original = Image.open(archivo).convert("RGB")
        ancho, alto = imagen_original.size
        procesar_y_mostrar()

def procesar_y_mostrar(event=None):
    if imagen_original is None: return

    # 1. Pipeline Base: Imagen Original -> Escala de Grises
    img_trabajo = imagen_original.copy()
    pix = img_trabajo.load()
    
    # --- FILTRO ADICIONAL 1: Saturación (Antes de grises para que se note) ---
    if usar_saturacion:
        enhancer = ImageEnhance.Color(img_trabajo)
        img_trabajo = enhancer.enhance(2.0) # Duplica la saturación
        pix = img_trabajo.load()

    # Convertir a Grises (Manual como en tus códigos)
    img_grises = Image.new("RGB", (ancho, alto))
    pix_grises = img_grises.load()
    for x in range(ancho):
        for y in range(alto):
            r, g, b = pix[x, y]
            gris = (r + g + b) // 3
            pix_grises[x, y] = (gris, gris, gris)

    # 2. Suavizado (Opcional)
    img_final_suavizado = img_grises
    if usar_suavizado:
        img_final_suavizado = Image.new("RGB", (ancho, alto))
        pix_s = img_final_suavizado.load()
        mask_s = [[1/9]*3 for _ in range(3)]
        for x in range(1, ancho-1):
            for y in range(1, alto-1):
                v = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        v += pix_grises[x+i, y+j][0] * mask_s[i+1][j+1]
                v = int(max(0, min(255, v)))
                pix_s[x, y] = (v, v, v)

    # 3. Detector de Bordes
    img_bordes = Image.new("RGB", (ancho, alto))
    pix_b = img_bordes.load()
    pix_in = img_final_suavizado.load()

    if metodo_bordes == 'Canny':
        # Nota: Canny es complejo, usamos una versión simplificada de tu lógica
        # Para mantener el flujo, procesamos el gradiente aquí
        gx_mask = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
        gy_mask = [[1, 2, 1], [0, 0, 0], [-1, -2, -1]]
    elif metodo_bordes == 'Prewitt':
        gx_mask = [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]
        gy_mask = [[-1, -1, -1], [0, 0, 0], [1, 1, 1]]
    elif metodo_bordes == 'Roberts':
        gx_mask = [[1, 0, 0], [0, -1, 0], [0, 0, 0]]
        gy_mask = [[0, 1, 0], [-1, 0, 0], [0, 0, 0]]
    else: # Sobel
        gx_mask = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
        gy_mask = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]

    for x in range(1, ancho-1):
        for y in range(1, alto-1):
            gx = gy = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    val = pix_in[x+i, y+j][0]
                    gx += val * gx_mask[j+1][i+1]
                    gy += val * gy_mask[j+1][i+1]
            mag = int(math.sqrt(gx**2 + gy**2))
            mag = max(0, min(255, mag))
            pix_b[x, y] = (mag, mag, mag)

    # --- FILTRO ADICIONAL 2: Laplaciano (Sobre los bordes o resultado final) ---
    if usar_laplaciano:
        img_lap = Image.new("RGB", (ancho, alto))
        pix_lap = img_lap.load()
        mask_l = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
        for x in range(1, ancho-1):
            for y in range(1, alto-1):
                suma = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        suma += pix_b[x+i, y+j][0] * mask_l[j+1][i+1]
                val = max(0, min(255, abs(suma)))
                pix_lap[x, y] = (val, val, val)
        img_bordes = img_lap

    # Actualizar Gráfica
    ax_orig.imshow(imagen_original)
    ax_res.imshow(img_bordes)
    plt.draw()

# --- Configuración de la Interfaz ---
fig, (ax_orig, ax_res) = plt.subplots(1, 2, figsize=(12, 6))
plt.subplots_adjust(bottom=0.3)

ax_orig.set_title("Entrada")
ax_res.set_title("Resultado del Pipeline")

# Botón Cargar
ax_btn = plt.axes([0.1, 0.15, 0.1, 0.05])
btn_load = Button(ax_btn, 'Cargar Imagen')
btn_load.on_clicked(cargar_imagen)

# Checkboxes para Opciones
ax_check = plt.axes([0.3, 0.05, 0.25, 0.15])
chks = CheckButtons(ax_check, ('Suavizado', 'Saturación (Extra)', 'Laplaciano (Extra)'), (False, False, False))

def actualizar_opciones(label):
    global usar_suavizado, usar_saturacion, usar_laplaciano
    if label == 'Suavizado': usar_suavizado = not usar_suavizado
    if label == 'Saturación (Extra)': usar_saturacion = not usar_saturacion
    if label == 'Laplaciano (Extra)': usar_laplaciano = not usar_laplaciano
    procesar_y_mostrar()
chks.on_clicked(actualizar_opciones)

# RadioButtons para elegir el detector
ax_radio = plt.axes([0.65, 0.05, 0.15, 0.15])
radio = RadioButtons(ax_radio, ('Sobel', 'Prewitt', 'Roberts', 'Canny'))

def cambiar_metodo(label):
    global metodo_bordes
    metodo_bordes = label
    procesar_y_mostrar()
radio.on_clicked(cambiar_metodo)

plt.show()