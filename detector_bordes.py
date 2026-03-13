# Interfaz unificada de detección de bordes
# Pipeline: Original -> Grises -> Suavizado (opcional) -> Detector -> Filtros adicionales (opcional)
# Filtros: Roberts, Prewitt, Sobel, Canny
# Filtros adicionales: Contraste, Laplaciano

from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Button, CheckButtons, RadioButtons
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import Tk
import math

# ─────────────────────────────────────────────────────────────────────────────
# Estado global
# ─────────────────────────────────────────────────────────────────────────────
imagen          = None
pixeles         = None
ancho, alto     = 100, 100

usar_suavizado  = False
usar_contraste  = False
usar_laplaciano = False
detector_actual = "Sobel"   # Roberts | Prewitt | Sobel | Canny

# Imágenes intermedias
img_grises      = None
img_suavizado   = None
img_resultado   = None   # imagen final del detector
img_extra       = None   # resultado tras filtros adicionales

direcciones_canny = []

# ─────────────────────────────────────────────────────────────────────────────
# Utilidades
# ─────────────────────────────────────────────────────────────────────────────

def nueva_img():
    return Image.new("RGB", (ancho, alto), color="white")

def nueva_img_negra():
    return Image.new("RGB", (ancho, alto), color="black")

def clamp(v, lo=0, hi=255):
    return min(max(int(v), lo), hi)

# ─────────────────────────────────────────────────────────────────────────────
# PASO 1 – Escala de grises
# ─────────────────────────────────────────────────────────────────────────────

def aplicar_grises(src_pix):
    global img_grises
    img_grises = nueva_img()
    pix = img_grises.load()
    for x in range(ancho):
        for y in range(alto):
            p = src_pix[x, y]
            g = (p[0] + p[1] + p[2]) // 3
            pix[x, y] = (g, g, g)

# ─────────────────────────────────────────────────────────────────────────────
# PASO 2 – Suavizado (media 3x3)
# ─────────────────────────────────────────────────────────────────────────────

def aplicar_suavizado(src_pix):
    global img_suavizado
    kernel = [[1/9]*3 for _ in range(3)]
    radio  = 1
    img_suavizado = nueva_img()
    pix = img_suavizado.load()
    for x in range(1, ancho - 1):
        for y in range(1, alto - 1):
            r = g = b = 0.0
            for j in range(-radio, radio + 1):
                for i in range(-radio, radio + 1):
                    p = src_pix[x + i, y + j]
                    w = kernel[j + radio][i + radio]
                    r += p[0] * w
                    g += p[1] * w
                    b += p[2] * w
            pix[x, y] = (clamp(r), clamp(g), clamp(b))
    # bordes: copiar pixel original
    for x in range(ancho):
        for y in range(alto):
            if pix[x, y] == (255, 255, 255) and src_pix[x, y] != (255, 255, 255):
                p = src_pix[x, y]
                g = (p[0] + p[1] + p[2]) // 3
                pix[x, y] = (g, g, g)

# ─────────────────────────────────────────────────────────────────────────────
# PASO 3 – Filtro adicional: Contraste
# ─────────────────────────────────────────────────────────────────────────────

def aplicar_contraste(pix_ref):
    """Aumenta el contraste multiplicando por 1.3 (en la imagen de grises)."""
    global img_grises
    pix = img_grises.load()
    for x in range(ancho):
        for y in range(alto):
            g = pix_ref[x, y][0]
            g = clamp(g * 1.3)
            pix[x, y] = (g, g, g)

# ─────────────────────────────────────────────────────────────────────────────
# DETECTORES
# ─────────────────────────────────────────────────────────────────────────────

def aplicar_convolucion(pix_in, kernel):
    """Devuelve una imagen nueva con la convolución aplicada (magnitud, sin combinar)."""
    radio = len(kernel) // 2
    out = nueva_img()
    pix_out = out.load()
    for x in range(radio, ancho - radio):
        for y in range(radio, alto - radio):
            n = 0
            for j in range(-radio, radio + 1):
                for i in range(-radio, radio + 1):
                    intensidad = pix_in[x + i, y + j][0]
                    n += intensidad * kernel[j + radio][i + radio]
            pix_out[x, y] = (clamp(n), clamp(n), clamp(n))
    return out

def combinar_gradientes(pix_gx, pix_gy):
    """Combina Gx y Gy con sqrt(Gx²+Gy²)."""
    out = nueva_img()
    pix = out.load()
    for x in range(ancho):
        for y in range(alto):
            gx = pix_gx[x, y][0]
            gy = pix_gy[x, y][0]
            n  = clamp(int((gx**2 + gy**2) ** 0.5))
            pix[x, y] = (n, n, n)
    return out

# ── Roberts ──────────────────────────────────────────────────────────────────

def detector_roberts(pix_in):
    gx_kernel = [[1, 0, 0], [0, -1, 0], [0, 0, 0]]
    gy_kernel = [[0, 1, 0], [-1, 0, 0], [0, 0, 0]]
    img_gx = aplicar_convolucion(pix_in, gx_kernel)
    img_gy = aplicar_convolucion(pix_in, gy_kernel)
    return combinar_gradientes(img_gx.load(), img_gy.load())

# ── Prewitt ───────────────────────────────────────────────────────────────────

def detector_prewitt(pix_in):
    gx_kernel = [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]
    gy_kernel = [[-1, -1, -1], [0, 0, 0], [1, 1, 1]]
    img_gx = aplicar_convolucion(pix_in, gx_kernel)
    img_gy = aplicar_convolucion(pix_in, gy_kernel)
    return combinar_gradientes(img_gx.load(), img_gy.load())

# ── Sobel ─────────────────────────────────────────────────────────────────────

def detector_sobel(pix_in):
    gx_kernel = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    gy_kernel = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
    img_gx = aplicar_convolucion(pix_in, gx_kernel)
    img_gy = aplicar_convolucion(pix_in, gy_kernel)
    return combinar_gradientes(img_gx.load(), img_gy.load())

# ── Canny ─────────────────────────────────────────────────────────────────────

def detector_canny(pix_in):
    global direcciones_canny

    # 1. Suavizado Gaussiano interno (3x3)
    mask_g = [[1, 2, 1], [2, 4, 2], [1, 2, 1]]
    radio_g = 1
    gaussiano = nueva_img()
    pg = gaussiano.load()
    for x in range(ancho):
        for y in range(alto):
            r = g = b = n = 0
            for dx in range(-radio_g, radio_g + 1):
                for dy in range(-radio_g, radio_g + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < ancho and 0 <= ny < alto:
                        p   = pix_in[nx, ny]
                        w   = mask_g[dx + radio_g][dy + radio_g]
                        r  += p[0] * w
                        g  += p[1] * w
                        b  += p[2] * w
                        n  += w
            if n == 0: n = 1
            pg[x, y] = (r // n, g // n, b // n)

    # 2. Gradiente con Sobel
    mask_x = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    mask_y = [[ 1, 2, 1], [ 0, 0, 0], [-1,-2,-1]]
    grad = nueva_img()
    p_grad = grad.load()
    dirs = [[0] * alto for _ in range(ancho)]
    for x in range(ancho):
        for y in range(alto):
            gx = gy = 0
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < ancho and 0 <= ny < alto:
                        val = pg[nx, ny][0]
                        gx += val * mask_x[dy + 1][dx + 1]
                        gy += val * mask_y[dy + 1][dx + 1]
            mag = clamp(int((gx**2 + gy**2) ** 0.5))
            ang = math.degrees(math.atan2(gy, gx))
            if ang < 0: ang += 180
            dirs[x][y] = ang
            p_grad[x, y] = (mag, mag, mag)
    direcciones_canny = dirs

    # 3. Supresión de no-máximos
    sup = nueva_img_negra()
    p_sup = sup.load()
    for x in range(1, ancho - 1):
        for y in range(1, alto - 1):
            mag = p_grad[x, y][0]
            ang = dirs[x][y]
            if   (0   <= ang < 22.5)  or (157.5 <= ang <= 180):
                v1, v2 = p_grad[x-1, y][0], p_grad[x+1, y][0]
            elif  22.5 <= ang < 67.5:
                v1, v2 = p_grad[x-1, y-1][0], p_grad[x+1, y+1][0]
            elif  67.5 <= ang < 112.5:
                v1, v2 = p_grad[x, y-1][0], p_grad[x, y+1][0]
            else:
                v1, v2 = p_grad[x-1, y+1][0], p_grad[x+1, y-1][0]
            if mag >= v1 and mag >= v2:
                p_sup[x, y] = (mag, mag, mag)

    # 4. Umbral doble
    umbral_alto, umbral_bajo = 100, 50
    umbral = nueva_img_negra()
    p_umb = umbral.load()
    for x in range(ancho):
        for y in range(alto):
            mag = p_sup[x, y][0]
            if   mag >= umbral_alto: p_umb[x, y] = (255, 255, 255)
            elif mag >= umbral_bajo: p_umb[x, y] = (100, 100, 100)

    # 5. Histéresis
    out = nueva_img_negra()
    p_out = out.load()
    for x in range(1, ancho - 1):
        for y in range(1, alto - 1):
            v = p_umb[x, y][0]
            if v == 255:
                p_out[x, y] = (255, 255, 255)
            elif v == 100:
                conectado = any(
                    p_umb[x + dx, y + dy][0] == 255
                    for dx in [-1, 0, 1] for dy in [-1, 0, 1]
                )
                p_out[x, y] = (255, 255, 255) if conectado else (0, 0, 0)
    return out

# ─────────────────────────────────────────────────────────────────────────────
# FILTRO ADICIONAL: Laplaciano (post-detector)
# ─────────────────────────────────────────────────────────────────────────────

def aplicar_laplaciano(pix_in):
    kernel = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
    out = nueva_img_negra()
    pix = out.load()
    for x in range(1, ancho - 1):
        for y in range(1, alto - 1):
            s = 0
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    s += kernel[dx + 1][dy + 1] * pix_in[x + dx, y + dy][0]
            pix[x, y] = (clamp(abs(s)),) * 3
    return out

# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def ejecutar_pipeline():
    global img_grises, img_suavizado, img_resultado, img_extra

    if imagen is None:
        return

    # Paso 1: Grises
    aplicar_grises(pixeles)

    # Paso 2 (opcional): Contraste ANTES de suavizado
    if usar_contraste:
        pix_ref = img_grises.load()
        aplicar_contraste(pix_ref)

    # Paso 3 (opcional): Suavizado
    if usar_suavizado:
        aplicar_suavizado(img_grises.load())
        pix_para_detector = img_suavizado.load()
    else:
        img_suavizado = None
        pix_para_detector = img_grises.load()

    # Paso 4: Detector
    if   detector_actual == "Roberts": img_resultado = detector_roberts(pix_para_detector)
    elif detector_actual == "Prewitt": img_resultado = detector_prewitt(pix_para_detector)
    elif detector_actual == "Sobel":   img_resultado = detector_sobel(pix_para_detector)
    elif detector_actual == "Canny":   img_resultado = detector_canny(pix_para_detector)

    # Paso 5 (opcional): Laplaciano POST-detector
    if usar_laplaciano:
        img_extra = aplicar_laplaciano(img_resultado.load())
    else:
        img_extra = None

    actualizar_vista()

# ─────────────────────────────────────────────────────────────────────────────
# VISUALIZACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def actualizar_vista():
    # Calcular cuántos pasos mostrar
    etapas = [("Original", imagen)]
    etapas.append(("Escala de Grises", img_grises))
    if usar_contraste:
        etapas.append(("+ Contraste", img_grises))
    if usar_suavizado and img_suavizado is not None:
        etapas.append(("Suavizado", img_suavizado))
    etapas.append((f"Detector:\n{detector_actual}", img_resultado))
    if usar_laplaciano and img_extra is not None:
        etapas.append(("+ Laplaciano", img_extra))

    n = len(etapas)
    for ax in axes:
        ax.clear()
        ax.axis("off")

    for idx, (titulo, img) in enumerate(etapas):
        if idx < len(axes):
            axes[idx].imshow(img)
            axes[idx].set_title(titulo, fontsize=9, pad=4)
            axes[idx].axis("off")

    # Pipeline label
    pasos = ["Original", "Grises"]
    if usar_contraste:  pasos.append("Contraste")
    if usar_suavizado:  pasos.append("Suavizado")
    pasos.append(detector_actual)
    if usar_laplaciano: pasos.append("Laplaciano")
    pipeline_txt = " → ".join(pasos)
    fig.suptitle(f"Pipeline:  {pipeline_txt}", fontsize=10, fontweight="bold", y=0.98)

    fig.canvas.draw_idle()

# ─────────────────────────────────────────────────────────────────────────────
# CALLBACKS DE CONTROLES
# ─────────────────────────────────────────────────────────────────────────────

def cb_cargar(event):
    global imagen, pixeles, ancho, alto
    Tk().withdraw()
    archivo = askopenfilename(
        title="Selecciona una imagen",
        filetypes=[("Imágenes", "*.jpg;*.jpeg;*.png;*.bmp")]
    )
    if not archivo:
        return
    imagen  = Image.open(archivo).convert("RGB")
    ancho, alto = imagen.size
    pixeles = imagen.load()
    ejecutar_pipeline()

def cb_suavizado(label):
    global usar_suavizado
    usar_suavizado = not usar_suavizado
    ejecutar_pipeline()

def cb_contraste(label):
    global usar_contraste
    usar_contraste = not usar_contraste
    ejecutar_pipeline()

def cb_laplaciano(label):
    global usar_laplaciano
    usar_laplaciano = not usar_laplaciano
    ejecutar_pipeline()

def cb_detector(label):
    global detector_actual
    detector_actual = label
    ejecutar_pipeline()

def cb_guardar(event):
    if img_extra is not None:
        img_guardar = img_extra
    elif img_resultado is not None:
        img_guardar = img_resultado
    else:
        return
    Tk().withdraw()
    ruta = asksaveasfilename(
        title="Guardar resultado",
        defaultextension=".png",
        filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
    )
    if ruta:
        img_guardar.save(ruta)
        print(f"Imagen guardada en: {ruta}")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURA
# ─────────────────────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(16, 7))
fig.patch.set_facecolor("#f0f0f0")

# Grid principal: columna izquierda de controles, columna derecha de imágenes
gs_main = gridspec.GridSpec(1, 2, width_ratios=[1, 4], wspace=0.05)

# Panel izquierdo de controles
gs_ctrl = gridspec.GridSpecFromSubplotSpec(
    7, 1, subplot_spec=gs_main[0], hspace=0.6
)

# Panel derecho de imágenes (máximo 6 etapas)
gs_imgs = gridspec.GridSpecFromSubplotSpec(
    1, 6, subplot_spec=gs_main[1], wspace=0.08
)
axes = [fig.add_subplot(gs_imgs[0, i]) for i in range(6)]
for ax in axes:
    ax.axis("off")

# ── Botón: Cargar imagen ──────────────────────────────────────────────────────
ax_cargar = fig.add_subplot(gs_ctrl[0])
ax_cargar.set_facecolor("#d0e8ff")
btn_cargar = Button(ax_cargar, "📂  Cargar imagen", color="#d0e8ff", hovercolor="#a0c8ff")
btn_cargar.label.set_fontsize(9)
btn_cargar.on_clicked(cb_cargar)

# ── Detector: RadioButtons ────────────────────────────────────────────────────
ax_radio = fig.add_subplot(gs_ctrl[1:4])
ax_radio.set_title("Detector de bordes", fontsize=9, pad=2)
radio_det = RadioButtons(
    ax_radio,
    ("Roberts", "Prewitt", "Sobel", "Canny"),
    active=2   # Sobel por defecto
)
for lbl in radio_det.labels:
    lbl.set_fontsize(9)
radio_det.on_clicked(cb_detector)

# ── Opciones: CheckButtons ────────────────────────────────────────────────────
ax_check = fig.add_subplot(gs_ctrl[4:6])
ax_check.set_title("Opciones del pipeline", fontsize=9, pad=2)
check_opts = CheckButtons(
    ax_check,
    ["Suavizado\n(pre-detector)", "Contraste\n(pre-detector)", "Laplaciano\n(post-detector)"],
    [False, False, False]
)
for lbl in check_opts.labels:
    lbl.set_fontsize(8)
check_opts.on_clicked(lambda label: (
    cb_suavizado(label)   if "Suavizado"  in label else
    cb_contraste(label)   if "Contraste"  in label else
    cb_laplaciano(label)
))

# ── Botón: Guardar ────────────────────────────────────────────────────────────
ax_guardar = fig.add_subplot(gs_ctrl[6])
ax_guardar.set_facecolor("#d0ffd8")
btn_guardar = Button(ax_guardar, "💾  Guardar resultado", color="#d0ffd8", hovercolor="#a0ffb0")
btn_guardar.label.set_fontsize(9)
btn_guardar.on_clicked(cb_guardar)

fig.suptitle("Pipeline: (carga una imagen para comenzar)", fontsize=10, fontweight="bold", y=0.98)
plt.show()
