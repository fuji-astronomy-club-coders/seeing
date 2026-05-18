import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, LinearSegmentedColormap

impath = r"J:\img1.tiff"
img = cv2.imread(impath, cv2.IMREAD_UNCHANGED).astype(np.float32)

# -----------------------------
# 横方向の二次微分 d²/dx²
# -----------------------------
height_x = img.shape[0] - 1
width_x = img.shape[1] - 2

dif_x_list = []
for i in range(1, img.shape[0]):
    dif_x_list.append(np.diff(np.diff(img[i])))

dif_x = np.concatenate(dif_x_list).reshape(height_x, width_x)

# -----------------------------
# 縦方向の二次微分 d²/dy²
# -----------------------------
height_y = img.shape[0] - 2
width_y = img.shape[1] - 1

dif_y_list = []
for j in range(1, img.shape[1]):
    col = img[:, j]  # 縦方向の列
    dif_y_list.append(np.diff(np.diff(col)))

dif_y = np.array(dif_y_list).T  # (height_y, width_y) に整形

# -----------------------------
# カラーマップ（横用）
# -----------------------------
cmap_neg = plt.cm.Blues_r
cmap_pos = plt.cm.Reds
colors = np.vstack((cmap_neg(np.linspace(0, 1, 128)),
                    cmap_pos(np.linspace(0, 1, 128))))
cmap_x = LinearSegmentedColormap.from_list("cmap_x", colors)

vmin_x, vmax_x = dif_x.min(), dif_x.max()
vmin_x, vcenter_x, vmax_x = sorted([vmin_x, 0, vmax_x])
norm_x = TwoSlopeNorm(vmin=vmin_x, vcenter=vcenter_x, vmax=vmax_x)

# -----------------------------
# カラーマップ（縦用）
# -----------------------------
cmap_neg2 = plt.cm.Greens_r
cmap_pos2 = plt.cm.Purples
colors2 = np.vstack((cmap_neg2(np.linspace(0, 1, 128)),
                     cmap_pos2(np.linspace(0, 1, 128))))
cmap_y = LinearSegmentedColormap.from_list("cmap_y", colors2)

vmin_y, vmax_y = dif_y.min(), dif_y.max()
vmin_y, vcenter_y, vmax_y = sorted([vmin_y, 0, vmax_y])
norm_y = TwoSlopeNorm(vmin=vmin_y, vcenter=vcenter_y, vmax=vmax_y)

# -----------------------------
# 描画
# -----------------------------
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.title("Horizontal 2nd Derivative (d²/dx²)")
plt.imshow(dif_x, cmap=cmap_x, norm=norm_x)
plt.colorbar()

plt.subplot(1, 2, 2)
plt.title("Vertical 2nd Derivative (d²/dy²)")
plt.imshow(dif_y, cmap=cmap_y, norm=norm_y)
plt.colorbar()

plt.tight_layout()
plt.show()
