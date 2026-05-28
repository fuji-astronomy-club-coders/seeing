import cv2
import sys
import KANSUU
import numpy as np
import matplotlib.pyplot as plt
from KANSUU import MIN2
"""
sengiriは、MIN2から得られた太陽の中心座標と半径をもとに、全周を上下左右に4等分し、太陽の縁±limb_wigthの範囲で実際の縁を探し、MIN2の縁との差のリストを返します。
基本的に
なお、差は、円の中心を通る水平または垂直な線との距離を比較して求めます。
各変数の意味は以下の通りです。
file: 画像ファイルのパス
gap: 各扇方の弧の端と扇型の中線の距離…78期生の偉大な雄が数えたら全周1360点らしく、それでやってます。default:170
limb_wigth: 太陽の縁からの距離。単位はピクセル。太陽の縁±limb_wigthの範囲で実際の縁を探します。default:24
"""
def where_sample(sample,place,gaps,tx,xc,yc,r,x_of,y_of,img):
    """主にdebug用です。sampleが画像上のどこなのかを見せてくれます。"""
    figure, ax = plt.subplots()
    ax.imshow(img, cmap='magma')
    ax.scatter( xc+np.mean(x_of), yc+np.mean(y_of), color='cyan', label='MIN edge', s=10)
    ax.plot( [xc+x_of[0],xc+x_of[1]],[yc+y_of[0],yc+y_of[1]], color='green', label='sample', alpha=0.5)
    import matplotlib.patches as patches
    circle = patches.Circle((xc, yc), r, fill=False, edgecolor='yellow', linewidth=2)
    ax.add_patch(circle)
    print(tx)
    print(int(yc+y_of[0]), int(yc+y_of[1]), int(xc+x_of[0]), int(xc+x_of[1]))
    plt.show(block=True)

