from pickle import FALSE
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, LinearSegmentedColormap

impath = r"J:\img1.tiff"
img = cv2.imread(impath, cv2.IMREAD_UNCHANGED).astype(np.float32)
diff2=True

# ============================
# MIN2（中心と半径）
# ============================
def MIN2(file):
    img = cv2.imread(file, 0)
    height, width = img.shape

    n=10
    div=[]
    for i in range(1, n):
        line_t = img[:, width * i // n].astype(float) 
        if np.max(line_t) <= 50:
            continue
        grad_t = np.diff(line_t)
        div.append([width*i//n, np.argmax(grad_t)])
        div.append([width*i//n, np.argmin(grad_t)])

    for i in range(1, n):
        line_p = img[height * i // n,:].astype(float)
        if np.max(line_p) <= 50:
            continue
        grad_p = np.diff(line_p)
        div.append([np.argmax(grad_p), height*i//n])
        div.append([np.argmin(grad_p), height*i//n])

    points = np.array(div, dtype=float)
    x = points[:, 0]
    y = points[:, 1]

    mat_A = np.c_[x, y, np.ones(len(x))]
    vec_B = -(x**2 + y**2)
    res, _, _, _ = np.linalg.lstsq(mat_A, vec_B, rcond=None)
    A, B, C = res

    cx = -A / 2
    cy = -B / 2
    r = np.sqrt(np.abs(cx**2 + cy**2 - C))
    return cx, cy, r

cx, cy, r = MIN2(impath)
cx = int(cx)
cy = int(cy)
r  = int(r)

# ============================
# dx, dy 計算（あなたのコードそのまま）
# ============================
height_x = img.shape[0] - 1
width_x = img.shape[1] - 1
dif_x_list = []
for i in range(1, img.shape[0]):
    dif_x_list.append(np.diff(img[i]))
if diff2:
    width_x -= 1
    for i in range(len(dif_x_list)):
        dif_x_list[i] = np.diff(dif_x_list[i])

dif_x = np.concatenate(dif_x_list).reshape(height_x, width_x)

height_y = img.shape[0] - 1
width_y = img.shape[1] - 1
dif_y_list = []
for j in range(1, img.shape[1]):
    dif_y_list.append(np.diff(img[:, j]))
if diff2:
    height_y -= 1
    for i in range(len(dif_y_list)):
        dif_y_list[i] = np.diff(dif_y_list[i])

dif_y = np.array(dif_y_list).T

H = min(dif_x.shape[0], dif_y.shape[0])
W = min(dif_x.shape[1], dif_y.shape[1])

dx = dif_x[:H, :W]
dy = dif_y[:H, :W]

# ============================
# カラーマップ（あなたのコードそのまま）
# ============================
cmap_x = LinearSegmentedColormap.from_list(
    "cmap_x",
    np.vstack((plt.cm.Blues_r(np.linspace(0,1,128)),
               plt.cm.Reds(np.linspace(0,1,128))))
)
vmin_x, vmax_x = dx.min(), dx.max()
vmin_x, vcenter_x, vmax_x = sorted([vmin_x, 0, vmax_x])
norm_x = TwoSlopeNorm(vmin=vmin_x, vcenter=vcenter_x, vmax=vmax_x)

cmap_y = LinearSegmentedColormap.from_list(
    "cmap_y",
    np.vstack((plt.cm.Greens_r(np.linspace(0,1,128)),
               plt.cm.Purples(np.linspace(0,1,128))))
)
vmin_y, vmax_y = dy.min(), dy.max()
vmin_y, vcenter_y, vmax_y = sorted([vmin_y, 0, vmax_y])
norm_y = TwoSlopeNorm(vmin=vmin_y, vcenter=vcenter_y, vmax=vmax_y)

rgb_x = cmap_x(norm_x(dx))[..., :3]
rgb_y = cmap_y(norm_y(dy))[..., :3]
overlay = 0.5 * rgb_x + 0.5 * rgb_y

# ============================
# ± r/√2 の帯方式で R/L/T/B の最大点を抽出
# ============================

abs_dx = np.abs(dx)
abs_dy = np.abs(dy)

# 帯の境界
y_min_RL = int(cy - r / np.sqrt(2))
y_max_RL = int(cy + r / np.sqrt(2))

x_min_TB = int(cx - r / np.sqrt(2))
x_max_TB = int(cx + r / np.sqrt(2))

# --- RL（各行） ---
R_x = []
R_y = []
L_x = []
L_y = []

for y in range(max(0, y_min_RL), min(H, y_max_RL)):

    # 左側（x < cx）
    left = abs_dx[y, :cx]
    if left.size > 0:
        xL = np.argmax(left)
        L_x.append(xL)
        L_y.append(y)

    # 右側（x > cx）
    right = abs_dx[y, cx:]
    if right.size > 0:
        xR = np.argmax(right) + cx
        R_x.append(xR)
        R_y.append(y)

# --- TB（各列） ---
T_x = []
T_y = []
B_x = []
B_y = []

for x in range(max(0, x_min_TB), min(W, x_max_TB)):

    # 上側（y < cy）
    up = abs_dy[:cy, x]
    if up.size > 0:
        yU = np.argmax(up)
        T_x.append(x)
        T_y.append(yU)

    # 下側（y > cy）
    down = abs_dy[cy:, x]
    if down.size > 0:
        yD = np.argmax(down) + cy
        B_x.append(x)
        B_y.append(yD)
# ============================
# 描画
# ============================
fig = plt.figure(figsize=(14, 6))

# メイン画像（大きく）
ax_main = fig.add_axes([0.05, 0.05, 0.75, 0.9])  # 左, 下, 幅, 高さ
ax_main.imshow(overlay)
ax_main.set_title("Solar Limb Detection (± r/√2 band method)")
ax_main.axis("off")

mak="+"
alph=.9
siz=10
# R/L/T/B の点をプロット（十字マーカー）
ax_main.plot(R_x, R_y, marker=mak, linestyle='none',
             markersize=siz, color='lime', alpha=alph)

ax_main.plot(L_x, L_y, marker=mak, linestyle='none',
             markersize=siz, color='magenta', alpha=alph)

ax_main.plot(T_x, T_y, marker=mak, linestyle='none',
             markersize=siz, color='cyan', alpha=alph)

ax_main.plot(B_x, B_y, marker=mak, linestyle='none',
             markersize=siz, color='orange', alpha=alph)

# --- カラーバー（右側の細い余白に配置） ---

# dx カラーバー
cax_dx = fig.add_axes([0.82, 0.55, 0.02, 0.35])  # x, y, width, height
fig.colorbar(
    plt.cm.ScalarMappable(norm=norm_x, cmap=cmap_x),
    cax=cax_dx
)
cax_dx.set_title("dx", fontsize=8)

# dy カラーバー
cax_dy = fig.add_axes([0.82, 0.10, 0.02, 0.35])
fig.colorbar(
    plt.cm.ScalarMappable(norm=norm_y, cmap=cmap_y),
    cax=cax_dy
)
cax_dy.set_title("dy", fontsize=8)

plt.show()
