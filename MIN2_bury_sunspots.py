
import cv2
import numpy as np

"""
最小二乗法による円の検出を行う関数を作成します。
黒点を誤検知していたので、たいようの内側を微分の値=0で埋めます。
"""

def MIN2_bury_sunspots(file,n=10,UNC=True):
    if UNC:
        img = cv2.imread(file, cv2.IMREAD_UNCHANGED)
    else:
        img = cv2.imread(file, 0)
    if img is None:
        raise FileNotFoundError("ファイルが見つかりません。パスを確認してください。")

    height, width = img.shape

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

