from pickle import FALSE
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, LinearSegmentedColormap

impath = r"J:\img1.tiff"
img = cv2.imread(impath, cv2.IMREAD_UNCHANGED).astype(np.float32)
diff2=False

def MIN2(file):
    img = cv2.imread(file, 0)
    if img is None:
        raise FileNotFoundError("ファイルが見つかりません。パスを確認してください。")

    height, width = img.shape

    n=10
    div=[]
    for i in range(1, n):
        line_t = img[:, width * i // n].astype(float) 
        if np.max(line_t) <= 50:
            continue
        grad_t = np.diff(line_t)
        p1_y = np.argmax(grad_t) # 最大値のインデックス(y座標)
        p2_y = np.argmin(grad_t) # 最小値のインデックス(y座標)
        x_pos = width * i //n
        p1 = [x_pos, p1_y]
        p2 = [x_pos, p2_y]
        div.append(p1)
        div.append(p2)
    for i in range(1, n):
        line_p = img[height * i // n,:].astype(float)
        if np.max(line_p) <= 50:
            continue
        grad_p = np.diff(line_p)
        p3_x = np.argmax(grad_p) # 最大値のインデックス(x座標)
        p4_x = np.argmin(grad_p) # 最小値のインデックス(x座標)
        y_pos = height * i // n
        p3 = [p3_x, y_pos]
        p4 = [p4_x, y_pos]
        div.append(p3)
        div.append(p4)

    #print (div)

    if len(div)<3:
        print ("点が足りません")
        exit()

    # --- 点達をまとめる ---
    points = np.array(div, dtype=float)
    x = points[:, 0]                                                                              
    y = points[:, 1]

    # --- 4. 最小二乗法 ---
    mat_A = np.c_[x, y, np.ones(len(x))]
    vec_B = -(x**2 + y**2)
    res, _, _, _ = np.linalg.lstsq(mat_A, vec_B, rcond=None)
    A, B, C = res

    a = -A / 2
    b = -B / 2
    # ルートの中が負にならないよう絶対値をとる（4点の配置が悪い場合用）
    R = np.sqrt(np.abs(a**2 + b**2 - C))
    return a, b, R
center=MIN2(impath)[0:2]
# 横方向の二次微分
height_x = img.shape[0] - 1
width_x = img.shape[1] - 1
dif_x_list = []
for i in range(1, img.shape[0]):
    dif_x_list.append(np.diff(img[i]))
if diff2:
    width_x -= 1  # 二次微分の場合はさらに1列減る
    for i in range(len(dif_x_list)):
        dif_x_list[i] = np.diff(dif_x_list[i])

dif_x = np.concatenate(dif_x_list).reshape(height_x, width_x)


# 縦方向の微分
height_y = img.shape[0] - 1
width_y = img.shape[1] - 1

dif_y_list = []
for j in range(1, img.shape[1]):
    col = img[:, j]
    dif_y_list.append(np.diff(col))
if diff2:
    height_y -= 1  # 二次微分の場合はさらに1行減る
    for i in range(len(dif_y_list)):
        dif_y_list[i] = np.diff(dif_y_list[i])

dif_y = np.array(dif_y_list).T  # (height_y, width_y)

# サイズを合わせる（共通部分）
H = min(dif_x.shape[0], dif_y.shape[0])
W = min(dif_x.shape[1], dif_y.shape[1])

dx = dif_x[:H, :W]
dy = dif_y[:H, :W]

# カラーマップ（横）

cmap_x = LinearSegmentedColormap.from_list(
    "cmap_x",
    np.vstack((plt.cm.Blues_r(np.linspace(0,1,128)),
               plt.cm.Reds(np.linspace(0,1,128))))
)

vmin_x, vmax_x = dx.min(), dx.max()
vmin_x, vcenter_x, vmax_x = sorted([vmin_x, 0, vmax_x])
norm_x = TwoSlopeNorm(vmin=vmin_x, vcenter=vcenter_x, vmax=vmax_x)


# カラーマップ（縦）
cmap_y = LinearSegmentedColormap.from_list(
    "cmap_y",
    np.vstack((plt.cm.Greens_r(np.linspace(0,1,128)),
               plt.cm.Purples(np.linspace(0,1,128))))
)

vmin_y, vmax_y = dy.min(), dy.max()
vmin_y, vcenter_y, vmax_y = sorted([vmin_y, 0, vmax_y])
norm_y = TwoSlopeNorm(vmin=vmin_y, vcenter=vcenter_y, vmax=vmax_y)


# カラーマップを RGB に変換
rgb_x = cmap_x(norm_x(dx))[..., :3]  # 横
rgb_y = cmap_y(norm_y(dy))[..., :3]  # 縦


# 透明度つきで重ねる
alpha = 0.5
overlay = rgb_x * alpha + rgb_y * alpha

#横の中心の左右での微分最大点
center_x = int(center[0])
hori_points_x = []
hori_points_y = []

left = dx[:, :center_x]
if not diff2:
    left = np.abs(left)
xL = np.argmax(left, axis=1)   # 各行の最大点
yL = np.arange(H)

right = dx[:, center_x:]
if not diff2:
    right = np.abs(right)
xR = np.argmax(right, axis=1) + center_x
yR = np.arange(H)


#縦の中心の上下での微分最大点
center_y = int(center[1])
vert_points_x = []
vert_points_y = []
up = dy[:center_y, :]
if not diff2:
    up = np.abs(up)
yU = np.argmax(up, axis=0)
xU = np.arange(W)
down = dy[center_y:, :]
if not diff2:
    down = np.abs(down)
yD = np.argmax(down, axis=0) + center_y
xD = np.arange(W)




# 描画（カラーバー付き）
fig = plt.figure(figsize=(14, 6))

# グリッド（メイン画像 + 2つのカラーバー）
gs = fig.add_gridspec(1, 3, width_ratios=[4, 0.4, 0.4])

# メイン画像
ax_main = fig.add_subplot(gs[0, 0])
ax_main.set_title("Overlay of d²/dx² (Blue-Red) and d²/dy² (Green-Purple)")
ax_main.imshow(overlay)
# 横 左
ax_main.scatter(xL, yL, c="yellow", s=10)

# 横 右
ax_main.scatter(xR, yR, c="orange", s=10)

# 縦 上
ax_main.scatter(xU, yU, c="cyan", s=10)

# 縦 下
ax_main.scatter(xD, yD, c="magenta", s=10)

ax_main.axis("off")

# 横方向カラーバー
ax_x = fig.add_subplot(gs[0, 1])
plt.colorbar(
    plt.cm.ScalarMappable(norm=norm_x, cmap=cmap_x),
    cax=ax_x
)
ax_x.set_title("Horizontal d²/dx²")

# 縦方向カラーバー
ax_y = fig.add_subplot(gs[0, 2])
plt.colorbar(
    plt.cm.ScalarMappable(norm=norm_y, cmap=cmap_y),
    cax=ax_y
)
ax_y.set_title("Vertical d²/dy²")

plt.tight_layout()
plt.show()
