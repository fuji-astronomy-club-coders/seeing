import cv2
import sys
import KANSUU
import numpy as np
import matplotlib.pyplot as plt
from KANSUU import MIN2

def where_sample(sample,place,gaps,tx,cx,cy,r,x_of,y_of,img):
    """主にdebug用です。sampleが画像上のどこなのかを見せてくれます。"""
    figure, ax = plt.subplots()
    ax.imshow(img, cmap='magma')
    ax.scatter( cx+np.mean(x_of), cy+np.mean(y_of), color='cyan', label='MIN edge', s=10)
    ax.plot( [cx+x_of[0],cx+x_of[1]],[cy+y_of[0],cy+y_of[1]], color='green', label='sample', alpha=0.5)
    import matplotlib.patches as patches
    circle = patches.Circle((cx, cy), r, fill=False, edgecolor='yellow', linewidth=2)
    ax.add_patch(circle)
    print(tx)
    print(int(cy+y_of[0]), int(cy+y_of[1]), int(cx+x_of[0]), int(cx+x_of[1]))
    plt.show(block=True)

def sengiri_white(img,ciclestat,limb_wigth,numof_allpoint):
    """
    img:読み込んで渡してください
    ciclstat:[cx,cy,R]
    limb_wigth:近似円からどれくらいの範囲で実縁を探すか、(近似円周上の点±limb_wigth)
    numof_allpoint:全周でいくつの点をサンプリングするかです。これは、今まで全周=1360点としていたことに由来します。
                    LRTBに分けるので、4の倍数でないと不具合が発生します。
                    僕的には中心をとおる傾きが１，－１の直線で円を分割したほうがよくねって思います。
    以前のように、円の検出を任せたりはしません、
    ただ、円に沿って近似円と実縁の差を返してくれればよいのです。
    なお、処理系はone_and_twodiffDROW.pyのfissecをもとにしています。
    """
    gap=int(numof_allpoint/8)#円の中心をとおる線からの±距離
    cx,cy,r=ciclestat
    lst=np.array([[]]*4)
    for gaps in range(-gap , gap):#同時並行でやります。
            
            #近似円の縁を探索
            gaps_r =int(np.sqrt(np.abs(r**2 - gaps**2)))
            #  memo img[top : bottom, left : right]
            
            #場所ごとに...
            pl=["L","R","T","B"]
            pldc={
                "L":(True,0),
                "R":(True,1),
                "T":(False,0),
                "B":(False,1)
                }
            xyof=[
                (gaps,gaps+1)
                ,[(-gaps_r-limb_wigth,-gaps_r+limb_wigth),(gaps_r-limb_wigth,gaps_r+limb_wigth)]
            ]#円の中心に加算することで、ふちの位置がわかる数値、場所ごとに使うものは異なります。
            
            for place in pl:
                pld = pldc[place]#毎回 "[]"で書くのめんどいから用意しています

                #----sampleの取得----
                if pld[0]:
                    y_of,x_of = xyof[0],xyof[1][pld[1]] 
                elif not pld[0]:
                    y_of,x_of = xyof[1][pld[1]],xyof[0]
                splrang=( int(cy+y_of[0]), int(cy+y_of[1]), int(cx+x_of[0]), int(cx+x_of[1]) )#sampleのindex
                #samplerangeが画像の範囲外になっていないか確認
                if splrang[0] < 0 or splrang[1] > img.shape[0] or splrang[2] < 0 or splrang[3] > img.shape[1]:
                    print("image shape:", img.shape)
                    print("sample range:", splrang)
                    optwidth=limb_wigth+min([img.shape[0]-(cy+y_of[1]),cy+y_of[0], img.shape[1]-(cx+x_of[1]), cx+x_of[0]])
                    print("suggested Optimal limb_wigth at this point:", int(optwidth))
                    raise IndexError(f"Sample range is out of image bounds for place: {place}, gap: {gaps}\nRead the termination message for details.")                
                sample=img[splrang[0]:splrang[1], splrang[2]:splrang[3]]
                #sampleの整形
                sample=np.array(np.ravel(sample))
                if bool(pld[1]):
                    sample=np.flip(sample)

                #----処理開始----
                #1回微分(firstのf)
                fd_sample = np.abs(np.gradient(sample))
                fMaxd_sample = np.amax(fd_sample)
                findex_Max_d_sample = np.where(fd_sample == fMaxd_sample)[0][0]
                if bool(pld[1]):
                    fd_sample=np.flip(fd_sample)
                ftruthindex_Max_d_sample = np.where(fd_sample == fMaxd_sample)[0][0]
                #2回微分
                d_sample = np.abs(np.gradient(np.gradient(sample)))
                rowd_sample = d_sample
                d_sample=d_sample[:findex_Max_d_sample]#1回微分の外側
                Maxd_sample=np.max(d_sample)
                if bool(pld[1]):
                    rowd_sample=np.flip(rowd_sample)
                index_Max_d_sample = np.where(rowd_sample == Maxd_sample)[0][0]
                if not bool(pld[1]):
                    index_Max_d_sample = 2*limb_wigth-index_Max_d_sample
                    ftruthindex_Max_d_sample = 2*limb_wigth-ftruthindex_Max_d_sample
                real_r = gaps_r - limb_wigth +index_Max_d_sample #limbまでの距離
                lst[pl.index(place)]+=np.array(real_r)
    relst=np.array()
    for l in lst:
        relst+=l
    return relst