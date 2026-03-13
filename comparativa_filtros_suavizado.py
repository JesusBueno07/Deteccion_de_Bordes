from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from tkinter.filedialog import askopenfilename
from tkinter import Tk
import math

Tk().withdraw()
archivo = askopenfilename(title="Selecciona una imagen", filetypes=[("Archivos de imagen", "*.jpg;*.jpeg;*.png")])

imagen = Image.open(archivo)
pixeles = imagen.load()
ancho, alto = imagen.size

# ── Escala de grises ──────────────────────────────────────────────────────────
grises = Image.new("RGB", (ancho, alto), color="white")
pixeles_grises = grises.load()
for x in range(ancho):
    for y in range(alto):
        p = pixeles[x, y]
        g = (p[0] + p[1] + p[2]) // 3
        pixeles_grises[x, y] = (g, g, g)

# ── Suavizado Gaussiano 3x3 ───────────────────────────────────────────────────
mask_g = [[1, 2, 1],
          [2, 4, 2],
          [1, 2, 1]]

suavizado = Image.new("RGB", (ancho, alto), color="white")
pixeles_suavizado = suavizado.load()
for x in range(ancho):
    for y in range(alto):
        r = g = b = n = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx2, ny2 = x+dx, y+dy
                if 0 <= nx2 < ancho and 0 <= ny2 < alto:
                    p = pixeles_grises[nx2, ny2]
                    w = mask_g[dx+1][dy+1]
                    r += p[0]*w; g += p[1]*w; b += p[2]*w; n += w
        if n == 0: n = 1
        pixeles_suavizado[x, y] = (r//n, g//n, b//n)

#A partir de aquí todos los filtros usan pixeles_suavizado
radio = 1

# ── ROBERTS ───────────────────────────────────────────────────────────────────
roberts_gx_k = [[1, 0, 0], [0, -1, 0], [0, 0, 0]]
roberts_gy_k = [[0, 1, 0], [-1, 0, 0], [0, 0, 0]]

img_roberts_gx = Image.new("RGB", (ancho, alto), color="white")
pix_roberts_gx = img_roberts_gx.load()
for x in range(1, ancho-1):
    for y in range(1, alto-1):
        n = 0
        for j in range(-radio, radio+1):
            for i in range(-radio, radio+1):
                n += pixeles_suavizado[x+i, y+j][0] * roberts_gx_k[j+radio][i+radio]
        pix_roberts_gx[x, y] = (min(max(n,0),255),)*3

img_roberts_gy = Image.new("RGB", (ancho, alto), color="white")
pix_roberts_gy = img_roberts_gy.load()
for x in range(1, ancho-1):
    for y in range(1, alto-1):
        n = 0
        for j in range(-radio, radio+1):
            for i in range(-radio, radio+1):
                n += pixeles_suavizado[x+i, y+j][0] * roberts_gy_k[j+radio][i+radio]
        pix_roberts_gy[x, y] = (min(max(n,0),255),)*3

filtro_roberts = Image.new("RGB", (ancho, alto), color="white")
pix_roberts = filtro_roberts.load()
for x in range(ancho):
    for y in range(alto):
        gx = pix_roberts_gx[x, y][0]
        gy = pix_roberts_gy[x, y][0]
        n = min(max(int((gx**2 + gy**2)**0.5), 0), 255)
        pix_roberts[x, y] = (n, n, n)

# ── PREWITT ───────────────────────────────────────────────────────────────────
prewitt_gx_k = [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]
prewitt_gy_k = [[-1, -1, -1], [0, 0, 0], [1, 1, 1]]

img_prewitt_gx = Image.new("RGB", (ancho, alto), color="white")
pix_prewitt_gx = img_prewitt_gx.load()
for x in range(1, ancho-1):
    for y in range(1, alto-1):
        n = 0
        for j in range(-radio, radio+1):
            for i in range(-radio, radio+1):
                n += pixeles_suavizado[x+i, y+j][0] * prewitt_gx_k[j+radio][i+radio]
        pix_prewitt_gx[x, y] = (min(max(n,0),255),)*3

img_prewitt_gy = Image.new("RGB", (ancho, alto), color="white")
pix_prewitt_gy = img_prewitt_gy.load()
for x in range(1, ancho-1):
    for y in range(1, alto-1):
        n = 0
        for j in range(-radio, radio+1):
            for i in range(-radio, radio+1):
                n += pixeles_suavizado[x+i, y+j][0] * prewitt_gy_k[j+radio][i+radio]
        pix_prewitt_gy[x, y] = (min(max(n,0),255),)*3

filtro_prewitt = Image.new("RGB", (ancho, alto), color="white")
pix_prewitt = filtro_prewitt.load()
for x in range(ancho):
    for y in range(alto):
        gx = pix_prewitt_gx[x, y][0]
        gy = pix_prewitt_gy[x, y][0]
        n = min(max(int((gx**2 + gy**2)**0.5), 0), 255)
        pix_prewitt[x, y] = (n, n, n)

# ── SOBEL ─────────────────────────────────────────────────────────────────────
sobel_gx_k = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
sobel_gy_k = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]

img_sobel_gx = Image.new("RGB", (ancho, alto), color="white")
pix_sobel_gx = img_sobel_gx.load()
for x in range(1, ancho-1):
    for y in range(1, alto-1):
        n = 0
        for j in range(-radio, radio+1):
            for i in range(-radio, radio+1):
                n += pixeles_suavizado[x+i, y+j][0] * sobel_gx_k[j+radio][i+radio]
        pix_sobel_gx[x, y] = (min(max(n,0),255),)*3

img_sobel_gy = Image.new("RGB", (ancho, alto), color="white")
pix_sobel_gy = img_sobel_gy.load()
for x in range(1, ancho-1):
    for y in range(1, alto-1):
        n = 0
        for j in range(-radio, radio+1):
            for i in range(-radio, radio+1):
                n += pixeles_suavizado[x+i, y+j][0] * sobel_gy_k[j+radio][i+radio]
        pix_sobel_gy[x, y] = (min(max(n,0),255),)*3

filtro_sobel = Image.new("RGB", (ancho, alto), color="white")
pix_sobel = filtro_sobel.load()
for x in range(ancho):
    for y in range(alto):
        gx = pix_sobel_gx[x, y][0]
        gy = pix_sobel_gy[x, y][0]
        n = min(max(int((gx**2 + gy**2)**0.5), 0), 255)
        pix_sobel[x, y] = (n, n, n)

# ── CANNY ─────────────────────────────────────────────────────────────────────
# Canny ya parte del suavizado gaussiano que hicimos arriba

# Gradiente con Sobel sobre la imagen ya suavizada
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
                    val = pixeles_suavizado[nx2, ny2][0]
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
filtro_canny = Image.new("RGB", (ancho, alto), color="black")
p_canny = filtro_canny.load()
for x in range(1, ancho-1):
    for y in range(1, alto-1):
        v = p_umb[x, y][0]
        if v == 255:
            p_canny[x, y] = (255,255,255)
        elif v == 100:
            conectado = any(p_umb[x+dx,y+dy][0]==255 for dx in [-1,0,1] for dy in [-1,0,1])
            p_canny[x, y] = (255,255,255) if conectado else (0,0,0)

# ── FIGURA ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(12, 7))

ax_original = fig.add_subplot(1, 2, 1)
ax_original.imshow(imagen)
ax_original.axis("off")
ax_original.set_title("Imagen Original", fontsize=11)

gs = gridspec.GridSpec(2, 2, figure=fig,
                       left=0.52, right=0.98,
                       top=0.92, bottom=0.05,
                       hspace=0.3, wspace=0.1)

ax_roberts = fig.add_subplot(gs[0, 0])
ax_roberts.imshow(filtro_roberts)
ax_roberts.axis("off")
ax_roberts.set_title("Roberts", fontsize=10)

ax_prewitt = fig.add_subplot(gs[0, 1])
ax_prewitt.imshow(filtro_prewitt)
ax_prewitt.axis("off")
ax_prewitt.set_title("Prewitt", fontsize=10)

ax_sobel = fig.add_subplot(gs[1, 0])
ax_sobel.imshow(filtro_sobel)
ax_sobel.axis("off")
ax_sobel.set_title("Sobel", fontsize=10)

ax_canny = fig.add_subplot(gs[1, 1])
ax_canny.imshow(filtro_canny)
ax_canny.axis("off")
ax_canny.set_title("Canny", fontsize=10)

plt.suptitle("Comparativa de detectores de bordes (con suavizado gaussiano)", fontsize=11)
plt.show()
