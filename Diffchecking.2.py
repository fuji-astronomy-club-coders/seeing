from pickle import FALSE
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, LinearSegmentedColormap

impath = r"J:\img1.tiff"
img = cv2.imread(impath, cv2.IMREAD_UNCHANGED).astype(np.float32)
diff2=True

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


# 描画（カラーバー付き）
fig = plt.figure(figsize=(14, 6))

# グリッド（メイン画像 + 2つのカラーバー）
gs = fig.add_gridspec(1, 3, width_ratios=[4, 0.4, 0.4])

# メイン画像
ax_main = fig.add_subplot(gs[0, 0])
ax_main.set_title("Overlay of d²/dx² (Blue-Red) and d²/dy² (Green-Purple)")
ax_main.imshow(overlay)
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
