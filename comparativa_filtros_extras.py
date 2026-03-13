from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.widgets import CheckButtons
from tkinter.filedialog import askopenfilename
from tkinter import Tk
import math

Tk().withdraw()
archivo = askopenfilename(title="Selecciona una imagen", filetypes=[("Archivos de imagen", "*.jpg;*.jpeg;*.png")])

imagen = Image.open(archivo).convert("RGB")
pixeles = imagen.load()
ancho, alto = imagen.size

usar_contraste  = False
usar_laplaciano = False

# ─────────────────────────────────────────────────────────────────────────────
# Funciones de procesamiento
# ─────────────────────────────────────────────────────────────────────────────

def hacer_grises(src):
    out = Image.new("RGB", (ancho, alto), color="white")
    pix = out.load()
    for x in range(ancho):
        for y in range(alto):
            p = src[x, y]
            g = (p[0] + p[1] + p[2]) // 3
            pix[x, y] = (g, g, g)
    return out

def hacer_contraste(src):
    out = Image.new("RGB", (ancho, alto), color="white")
    pix = out.load()
    for x in range(ancho):
        for y in range(alto):
            g = min(max(int(src[x, y][0] * 1.3), 0), 255)
            pix[x, y] = (g, g, g)
    return out

def hacer_gaussiano(src):
    mask = [[1,2,1],[2,4,2],[1,2,1]]
    out = Image.new("RGB", (ancho, alto), color="white")
    pix = out.load()
    for x in range(ancho):
        for y in range(alto):
            r = g = b = n = 0
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx2, ny2 = x+dx, y+dy
                    if 0 <= nx2 < ancho and 0 <= ny2 < alto:
                        p = src[nx2, ny2]
                        w = mask[dx+1][dy+1]
                        r += p[0]*w; g += p[1]*w; b += p[2]*w; n += w
            if n == 0: n = 1
            pix[x, y] = (r//n, g//n, b//n)
    return out

def convolucionar(src, kernel):
    radio = len(kernel) // 2
    out = Image.new("RGB", (ancho, alto), color="white")
    pix = out.load()
    for x in range(radio, ancho - radio):
        for y in range(radio, alto - radio):
            n = 0
            for j in range(-radio, radio+1):
                for i in range(-radio, radio+1):
                    n += src[x+i, y+j][0] * kernel[j+radio][i+radio]
            pix[x, y] = (min(max(n,0),255),)*3
    return out

def combinar_gx_gy(pix_gx, pix_gy):
    out = Image.new("RGB", (ancho, alto), color="white")
    pix = out.load()
    for x in range(ancho):
        for y in range(alto):
            gx = pix_gx[x, y][0]
            gy = pix_gy[x, y][0]
            n = min(max(int((gx**2 + gy**2)**0.5), 0), 255)
            pix[x, y] = (n, n, n)
    return out

def hacer_roberts(src):
    gx = convolucionar(src, [[1,0,0],[0,-1,0],[0,0,0]])
    gy = convolucionar(src, [[0,1,0],[-1,0,0],[0,0,0]])
    return combinar_gx_gy(gx.load(), gy.load())

def hacer_prewitt(src):
    gx = convolucionar(src, [[-1,0,1],[-1,0,1],[-1,0,1]])
    gy = convolucionar(src, [[-1,-1,-1],[0,0,0],[1,1,1]])
    return combinar_gx_gy(gx.load(), gy.load())

def hacer_sobel(src):
    gx = convolucionar(src, [[-1,0,1],[-2,0,2],[-1,0,1]])
    gy = convolucionar(src, [[-1,-2,-1],[0,0,0],[1,2,1]])
    return combinar_gx_gy(gx.load(), gy.load())

def hacer_canny(src):
    # Gradiente
    mask_x = [[-1,0,1],[-2,0,2],[-1,0,1]]
    mask_y = [[1,2,1],[0,0,0],[-1,-2,-1]]
    grad = Image.new("RGB", (ancho, alto), color="white")
    p_grad = grad.load()
    dirs = [[0]*alto for _ in range(ancho)]
    for x in range(ancho):
        for y in range(alto):
            gx = gy = 0
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx2, ny2 = x+dx, y+dy
                    if 0 <= nx2 < ancho and 0 <= ny2 < alto:
                        val = src[nx2, ny2][0]
                        gx += val * mask_x[dy+1][dx+1]
                        gy += val * mask_y[dy+1][dx+1]
            mag = min(max(int((gx**2+gy**2)**0.5), 0), 255)
            ang = math.degrees(math.atan2(gy, gx))
            if ang < 0: ang += 180
            dirs[x][y] = ang
            p_grad[x, y] = (mag, mag, mag)
    # Supresion de no maximos
    sup = Image.new("RGB", (ancho, alto), color="black")
    p_sup = sup.load()
    for x in range(1, ancho-1):
        for y in range(1, alto-1):
            mag = p_grad[x, y][0]
            ang = dirs[x][y]
            if   (0 <= ang < 22.5) or (157.5 <= ang <= 180):
                v1, v2 = p_grad[x-1,y][0], p_grad[x+1,y][0]
            elif 22.5 <= ang < 67.5:
                v1, v2 = p_grad[x-1,y-1][0], p_grad[x+1,y+1][0]
            elif 67.5 <= ang < 112.5:
                v1, v2 = p_grad[x,y-1][0], p_grad[x,y+1][0]
            else:
                v1, v2 = p_grad[x-1,y+1][0], p_grad[x+1,y-1][0]
            if mag >= v1 and mag >= v2:
                p_sup[x, y] = (mag, mag, mag)
    # Umbral doble
    umbral_alto, umbral_bajo = 100, 50
    umbral = Image.new("RGB", (ancho, alto), color="black")
    p_umb = umbral.load()
    for x in range(ancho):
        for y in range(alto):
            mag = p_sup[x, y][0]
            if   mag >= umbral_alto: p_umb[x, y] = (255,255,255)
            elif mag >= umbral_bajo: p_umb[x, y] = (100,100,100)
    # Histeresis
    out = Image.new("RGB", (ancho, alto), color="black")
    p_out = out.load()
    for x in range(1, ancho-1):
        for y in range(1, alto-1):
            v = p_umb[x, y][0]
            if v == 255:
                p_out[x, y] = (255,255,255)
            elif v == 100:
                conectado = any(p_umb[x+dx,y+dy][0]==255 for dx in [-1,0,1] for dy in [-1,0,1])
                p_out[x, y] = (255,255,255) if conectado else (0,0,0)
    return out

def hacer_laplaciano(src):
    kernel = [[0,1,0],[1,-4,1],[0,1,0]]
    out = Image.new("RGB", (ancho, alto), color="black")
    pix = out.load()
    for x in range(1, ancho-1):
        for y in range(1, alto-1):
            s = 0
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    s += kernel[dx+1][dy+1] * src[x+dx, y+dy][0]
            pix[x, y] = (min(max(abs(s),0),255),)*3
    return out

# ─────────────────────────────────────────────────────────────────────────────
# Pipeline y actualización
# ─────────────────────────────────────────────────────────────────────────────

def ejecutar_y_actualizar():
    # Grises
    img_grises = hacer_grises(pixeles)

    # Contraste (pre-detector)
    if usar_contraste:
        img_grises = hacer_contraste(img_grises.load())

    # Gaussiano
    img_suav = hacer_gaussiano(img_grises.load())
    pix_suav = img_suav.load()

    # 4 detectores
    r_roberts = hacer_roberts(pix_suav)
    r_prewitt  = hacer_prewitt(pix_suav)
    r_sobel    = hacer_sobel(pix_suav)
    r_canny    = hacer_canny(pix_suav)

    # Laplaciano (post-detector)
    if usar_laplaciano:
        r_roberts = hacer_laplaciano(r_roberts.load())
        r_prewitt  = hacer_laplaciano(r_prewitt.load())
        r_sobel    = hacer_laplaciano(r_sobel.load())
        r_canny    = hacer_laplaciano(r_canny.load())

    # Armar título del pipeline
    pasos = ["Grises"]
    if usar_contraste:  pasos.append("Contraste")
    pasos.append("Gaussiano")
    pasos.append("Detector")
    if usar_laplaciano: pasos.append("Laplaciano")
    titulo = "Pipeline: " + " → ".join(pasos)

    # Actualizar plots
    ax_roberts.imshow(r_roberts); ax_roberts.set_title("Roberts", fontsize=10)
    ax_prewitt.imshow(r_prewitt);  ax_prewitt.set_title("Prewitt", fontsize=10)
    ax_sobel.imshow(r_sobel);      ax_sobel.set_title("Sobel", fontsize=10)
    ax_canny.imshow(r_canny);      ax_canny.set_title("Canny", fontsize=10)
    fig.suptitle(titulo, fontsize=11)
    fig.canvas.draw_idle()

def cb_check(label):
    global usar_contraste, usar_laplaciano
    if label == "Contraste":
        usar_contraste  = not usar_contraste
    elif label == "Laplaciano":
        usar_laplaciano = not usar_laplaciano
    ejecutar_y_actualizar()

# ─────────────────────────────────────────────────────────────────────────────
# Figura
# ─────────────────────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(13, 7))

# Imagen original (izquierda)
ax_original = fig.add_axes([0.01, 0.15, 0.22, 0.75])
ax_original.imshow(imagen)
ax_original.axis("off")
ax_original.set_title("Imagen Original", fontsize=11)

# Checkboxes debajo de la imagen original
ax_check = fig.add_axes([0.04, 0.02, 0.18, 0.12])
check = CheckButtons(ax_check, ["Contraste", "Laplaciano"], [False, False])
for lbl in check.labels:
    lbl.set_fontsize(9)
check.on_clicked(cb_check)

# Cuadrícula 2x2 de filtros (derecha)
gs = gridspec.GridSpec(2, 2, figure=fig,
                       left=0.27, right=0.99,
                       top=0.92, bottom=0.05,
                       hspace=0.25, wspace=0.08)

ax_roberts = fig.add_subplot(gs[0, 0]); ax_roberts.axis("off")
ax_prewitt  = fig.add_subplot(gs[0, 1]); ax_prewitt.axis("off")
ax_sobel    = fig.add_subplot(gs[1, 0]); ax_sobel.axis("off")
ax_canny    = fig.add_subplot(gs[1, 1]); ax_canny.axis("off")

# Correr pipeline inicial
ejecutar_y_actualizar()

plt.show()
