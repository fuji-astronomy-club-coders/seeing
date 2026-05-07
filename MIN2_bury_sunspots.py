
import cv2
import numpy as np

"""
最小二乗法による円の検出を行う関数を作成します。
黒点を誤検知していたので、たいようの内側を微分の値=0で埋めます。
"""

def bury_line(img,whichxy,place):

def cut_and_smpling(img,n,sun_threshold):#imgの画像をnで分割、太陽の縁の点をsampling
    #画像を分割して実際の縁の点を収集
    div=[]
    for line in ("x_line","y_line"):
        for i in range(1,n)

    for i in range(1, n):#y方向の分割線
        line_t = img[:, width * i // n].astype(float) 
        #明るさの最大値に閾値をつけてその線が太陽像上を通るかを判定
        if np.max(line_t) <= sun_threshold:            
            continue
        grad_t = np.diff(line_t)
        p1_y = np.argmax(grad_t) # 最大値のインデックス(y座標)
        p2_y = np.argmin(grad_t) # 最小値のインデックス(y座標)
        x_pos = width * i //n
        p1 = [x_pos, p1_y]
        p2 = [x_pos, p2_y]
        div.append(p1)
        div.append(p2)
    for i in range(1, n):#x方向の分割線
        line_p = img[height * i // n,:].astype(float)
        if np.max(line_p) <= sun_threshold:
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
    return x,y

def fit_circle(spots):#縁の点のサンプルを受け取って円のstatusを返す。
    x,y=spots[0],spots[1]
    mat_A = np.c_[x, y, np.ones(len(x))]
    vec_B = -(x**2 + y**2)
    res, _, _, _ = np.linalg.lstsq(mat_A, vec_B, rcond=None)
    A, B, C = res
    cx = -A / 2
    cy = -B / 2
    R = np.sqrt(cx**2 + cy**2 - C)
    return [cx,cy,R]

def show_circle(img,cir_stat,n,x,y):
    cx,cy,R=cir_stat[0],cir_stat[1],cir_stat[2]
    fig, ax = plt.subplots()#figとaxの作成
        ax.imshow(img, cmap="gray")#画像をグレースケールで表示
        ax.imshow(img, cmap="viridis")#画像をviridisで表示
        circle = plt.Circle((cx, cy), R, fill=False, color='orange', linewidth=2)#結果の円を描画
        ax.add_patch(circle)###

        #各縁の点を描画
        ax.scatter(x, y, color='red', label='Edges', s=50)
        # 座標ラベルを表示
        for xi, yi in zip(x, y):
            ax.text(xi, yi, f"({xi:.0f}, {yi:.0f})",
                    color="#8917fd", fontsize=8,
                    ha="left", va="bottom")

        #画像の分割線を描画
        lines=[]
        for xy in ["x","y"]:#各分割線のlistを作成
            lines.append([])
            for nn in range(n) :
                ap=width/n if xy =="x" else height/n
                lines[-1].append(ap*(nn+1))
        for li in lines[0]:#x方向の分割線を描画
            ax.axvline(int(li), color='white', linestyle='--', alpha=0.3)
        for li in lines[1]:#y方向の分割線を描画
            ax.axhline(int(li), color='white', linestyle='--', alpha=0.3)

        # nの値を左上に固定表示
        ax.text(.05,.9, f"n={n}",
                color="cyan", fontsize=10,
                transform=ax.transAxes)
        ax.legend()###
        ax.axis('equal')###
        plt.show()#windowで表示

def MIN2_bury_sunspots(file,n=10,UNC=True):#from second pictures
    global cir_stat
    global img
    global n

    if UNC:#unchange
            img = cv2.imread(file, cv2.IMREAD_UNCHANGED)
        else:
            img = cv2.imread(file, 0)
        if img is None:
            raise FileNotFoundError("ファイルが見つかりません。パスを確認してください。")
        height, width = img.shape

    x,y=fit_circle(cut_and_smpling(img,n,50))