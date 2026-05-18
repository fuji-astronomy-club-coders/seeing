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
# rdx, rdy 計算
# ============================
#rdxの計算
rheight_x = img.shape[0]
rwidth_x  = img.shape[1] - 2   # ← これが正しい
width_x=img.shape[1] -1
rdif_x_list = []
for i in range(1, img.shape[0]):
    line = np.diff(img[i])          # 長さ = width - 1
    if diff2:
        line = np.diff(line)        # 長さ = width - 2
    rdif_x_list.append(line)

rdif_x = np.vstack(rdif_x_list)     # reshape 不要

dif_x = np.vstack(rdif_x_list) 

#rdyの計算
height_y = img.shape[0] - 1
rwidth_y = img.shape[1] - 1
rdif_y_list = []
dif_y_list = []
for j in range(1, img.shape[1]):
    rdif_y_list.append(np.diff(img[:, j]))
    dif_y_list.append(np.diff(img[:, j]))
if diff2:
    rheight_y =height_y - 1
    for i in range(len(rdif_y_list)):
        rdif_y_list[i] = np.diff(rdif_y_list[i])

rdif_y = np.array(rdif_y_list).T
dif_y = np.array(dif_y_list).T


dH = min(dif_x.shape[0], dif_y.shape[0])
dW = min(dif_x.shape[1], dif_y.shape[1])

dx = dif_x[:dH, :dW]
dy = dif_y[:dH, :dW]

H = min(rdif_x.shape[0], rdif_y.shape[0])
W = min(rdif_x.shape[1], rdif_y.shape[1])

rdx = rdif_x[:H, :W]
rdy = rdif_y[:H, :W]

# ============================
# カラーマップ（あなたのコードそのまま）
# ============================
cmap_x = LinearSegmentedColormap.from_list(
    "cmap_x",
    np.vstack((plt.cm.Blues_r(np.linspace(0,1,128)),
               plt.cm.Reds(np.linspace(0,1,128))))
)
vmin_x, vmax_x = rdx.min(), rdx.max()
vmin_x, vcenter_x, vmax_x = sorted([vmin_x, 0, vmax_x])
norm_x = TwoSlopeNorm(vmin=vmin_x, vcenter=vcenter_x, vmax=vmax_x)

cmap_y = LinearSegmentedColormap.from_list(
    "cmap_y",
    np.vstack((plt.cm.Greens_r(np.linspace(0,1,128)),
               plt.cm.Purples(np.linspace(0,1,128))))
)
vmin_y, vmax_y = rdy.min(), rdy.max()
vmin_y, vcenter_y, vmax_y = sorted([vmin_y, 0, vmax_y])
norm_y = TwoSlopeNorm(vmin=vmin_y, vcenter=vcenter_y, vmax=vmax_y)

rgb_x = cmap_x(norm_x(rdx))[..., :3]
rgb_y = cmap_y(norm_y(rdy))[..., :3]
overlay = 0.5 * rgb_x + 0.5 * rgb_y

# ============================
# ± r/√2 の帯方式で R/L/T/B の最大点を抽出
# ============================

abs_rdx = np.abs(rdx)
abs_rdy = np.abs(rdy)

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
    #一回微分の最大値
    dleft = np.abs(dx)[y, :cx]
    if dleft.size > 0:
        dxL = np.argmax(dleft)
    #一回微分の最大値の外側で二回微分の最大値
    left = abs_rdx[y, :dxL]
    if left.size > 0:
        xL = np.argmax(left)
        L_x.append(xL)
        L_y.append(y)

# 右側（x > cx）
    #一回微分の最大値
    dright = np.abs(dx)[y, :cx]
    if dright.size > 0:
        dxR = np.argmax(dright)
    #一回微分の最大値の外側で二回微分の最大値
    right = abs_rdx[y, dxR:]
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
    #一回微分の最大値
    dup = abs_rdy[:cy, x]
    if dup.size > 0:
        dyU = np.argmax(dup)
    up = abs_rdy[dyU:, x]
    #一回微分の最大値の外側で二回微分の最大値
    if up.size > 0:
        yU = np.argmax(up)
        T_x.append(x)
        T_y.append(yU)

# 下側（y > cy）
    #一回微分の最大値
    ddown = abs_rdy[cy:, x]
    if ddown.size > 0:
        dyD = np.argmax(ddown) + cy
    down = abs_rdy[dyD:, x]
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

# rdx カラーバー
cax_rdx = fig.add_axes([0.82, 0.55, 0.02, 0.35])  # x, y, width, height
fig.colorbar(
    plt.cm.ScalarMappable(norm=norm_x, cmap=cmap_x),
    cax=cax_rdx
)
cax_rdx.set_title("rdx", fontsize=8)

# rdy カラーバー
cax_rdy = fig.add_axes([0.82, 0.10, 0.02, 0.35])
fig.colorbar(
    plt.cm.ScalarMappable(norm=norm_y, cmap=cmap_y),
    cax=cax_rdy
)
cax_rdy.set_title("rdy", fontsize=8)

plt.show()
