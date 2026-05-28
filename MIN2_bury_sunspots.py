
import cv2
import numpy as np
import matplotlib.pyplot as plt
from KANSUU import cash 
"""
最小二乗法による円の検出を行う関数を作成します。
黒点を誤検知していたので、たいようの内側を微分の値=0で埋めます。
"""

def bury_line(line,iwhichxy,place):
    """line:分割線に沿った画素値の配列, iwhichxy:分割線の方向, place:分割線の位置"""
    #画像上のlineとおなじ位置のlistで、mask_cir_statと重なる範囲は0,それ以外は1のmaskを作成して、lineにかけることで、太陽の内側を埋める。
    mask=[1]*width if iwhichxy=="x_line" else [1]*height
    if iwhichxy=="x_line":#x_lineならば、placeはy座標、iはx座標
        for i in range(width):
            if (place-mask_cir_stat[1])**2+(i-mask_cir_stat[0])**2 < mask_cir_stat[2]**2:
                mask[i]=0
    elif iwhichxy=="y_line":#y_lineならば、placeはx座標、iはy座標
        for i in range(height):
            if (i-mask_cir_stat[1])**2+(place-mask_cir_stat[0])**2 < mask_cir_stat[2]**2:
                mask[i]=0
    return np.array(mask)*line#maskをかけることで、太陽の内側を埋める。 

def cut_and_smpling(sun_threshold):#imgの画像をnで分割、太陽の縁の点をsampling
    #画像を分割して実際の縁の点を収集
    div=[]
    points=np.array([])#実際の縁の点を格納するための配列
    for line_xy in ("x_line","y_line"):#x_lineは横線、y_lineは縦線
        for i in range(1,divnum):
            place = height * i // divnum      if line_xy == "x_line" else width * i // divnum#分割線の位置を計算
            line = img[place,:].astype(float) if line_xy == "x_line" else img[:, place].astype(float)#分割線に沿った画素値を取得
            if np.max(line) <= sun_threshold:#太陽像上を通るか
                continue
            line=bury_line(line,line_xy,place)#分割線をmethodに沿ってゼロ埋め
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

def show_circle(spots):#円のstatusを受け取って、画像に円と縁の点を描画して表示する。
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

def MIN2_bury_sunspots(file,n=10,UNC=True,mask=None,show=False):#from second pictures
    """
    mask:太陽の内側を埋めるための円の情報[cx, cy, R]をカンマ区切りの文字列で受け取る。例: "100,150,50"
    もしmaskがNoneならば、mask_cir_stat=[0,0,0]とする。
    """
    #===基本的な変数をglobalで宣言===
    global divnum#分割数、引数ではnとして受け取っている。
    divnum=n
    
    global img#読み込んだ画像
    if UNC:#unchange
        img = cv2.imread(file, cv2.IMREAD_UNCHANGED)
    else:
        img = cv2.imread(file, 0)
    if img is None:
        raise FileNotFoundError("ファイルが見つかりません。パスを確認してください。")
    
    global height, width#画像の高さと幅
    height, width = img.shape

    global mask_cir_stat#太陽の内側を埋めるための円の情報[cx, cy, R]
    mask_cir_stat = mask 
    global cir_stat#円の情報[cx, cy, R]
    spots=cut_and_smpling(50)
    cir_stat=fit_circle(spots)
    if type(mask)==str:
        print(mask)
    if show:
        show_circle(spots)
    return cir_stat