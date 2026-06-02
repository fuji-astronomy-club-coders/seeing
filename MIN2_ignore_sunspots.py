
import cv2
import numpy as np
import matplotlib.pyplot as plt
"""
最小二乗法による円の検出を行う関数を作成します。
一度検出した近似円の内側にある点のうち、近似円の外側にある点だけから近似した円からlimbwigth*(3/2)の
範囲にないもんは黒点とみなします。
"""

def cut_and_sampling(sun_threshold):#imgの画像をnで分割、太陽の縁の点をsampling
    #画像を分割して実際の縁の点を収集
    div=[]
    points=np.array([])#実際の縁の点を格納するための配列
    for line_xy in ("x_line","y_line"):#x_lineは横線、y_lineは縦線
        for i in range(1,divnum):
            place = height * i // divnum      if line_xy == "x_line" else width * i // divnum#分割線の位置を計算
            line = img[place,:].astype(float) if line_xy == "x_line" else img[:, place].astype(float)#分割線に沿った画素値を取得
            if np.max(line) <= sun_threshold:#太陽像上を通るか
                continue
            grad_t = np.diff(line)#一回微分
            max_idx = np.argmax(grad_t) # 最大値のインデックス
            min_idx = np.argmin(grad_t) # 最小値のインデックス
            if line_xy=="x_line":
                points.append(np.array([max_idx, place]))
                points.append(np.array([min_idx, place]))
            elif line_xy=="y_line":
                points.append(np.array([place, max_idx]))
                points.append(np.array([place, min_idx]))
    return points[:,0], points[:,1]#縁の点の座標を返す

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

def show_circle(spots,cir_stat):#円のstatusを受け取って、画像に円と縁の点を描画して表示する。
    x,y=spots[0],spots[1]
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
        for nn in range(divnum) :
            ap=width/divnum if xy =="x" else height/divnum
            lines[-1].append(ap*(nn+1))
    for li in lines[0]:#x方向の分割線を描画
        ax.axvline(int(li), color='white', linestyle='--', alpha=0.3)
    for li in lines[1]:#y方向の分割線を描画
        ax.axhline(int(li), color='white', linestyle='--', alpha=0.3)

    # nの値を左上に固定表示
    ax.text(.05,.9, f"n={divnum}",
            color="cyan", fontsize=10,
            transform=ax.transAxes)
    ax.legend()###
    ax.axis('equal')###
    plt.show()#windowで表示

def MIN2_bury_sunspots(readed_img,n=10,light_threshold=50,limb_wigth=24,show=False):
    """
    img:読み込んだ画像を渡してください
    n:画像格子の分割数
    light_threshold:太陽の明るさの基準です。

    """
    #===基本的な変数をglobalで宣言===
    global divnum#分割数、引数ではnとして受け取っている。
    divnum=n
    
    global img#読み込んだ画像
    img=readed_img
    global height, width#画像の高さと幅
    height, width = img.shape
    
    #円の情報[cx, cy, R]
    spots=cut_and_sampling(light_threshold)
    cx,cy,r=fit_circle(spots)#一回目の円情報

    outside_spots_idx=[]#一回目のMIN2の外側の点の番号を取得
    for i in range(len(spots)):
        if int(((spots[0][i]-cx)**2+(spots[1][i]-cy)**2)**(1/2))>r:
            outside_spots_idx+=[i]
    
    cxo,cyo,ro=fit_circle([spots[0][i] for i in outside_spots_idx],[spots[1][i] for i in outside_spots_idx])#外側の点だけで円を作成

    not_sunspots_idx=[]
    for i in range(len(spots[0])):
        x=spots[0][i]
        y=spots[1][i]
        if not i in outside_spots_idx:#内側の点だけ
            if (x-cx)**2 > (y-cy)**2:#円のRLTBのうちRLなら、
                min2far = ((y-cyo)**2/ro**2)**(1/2)
                if min2far-x > limb_wigth:
                    sunspots_idx+=[i]
            else:#円のRLTBのうちTBなら
                min2far = ((x-cxo)**2/ro**2)**(1/2)
                if min2far-y > limb_wigth:
                    sunspots_idx+=[i]
    if len(not_sunspots_idx) <3 :
        show_circle(spots,(cx,cy,r))
        raise("点不足,nが小さすぎるか、黒点が多すぎ")
    cx,cy,r=fit_circle([spots[0][i] for i in not_sunspots_idx],[spots[1][i] for i in not_sunspots_idx])

    if show:
        show_circle(spots,(cx,cy,r))
    return cx,cy,r