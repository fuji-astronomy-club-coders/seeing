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
def sengiri_X2_GetERO(
    file
    ,gap=170
    ,limb_wigth = 24
    ):
    """ 
    IOORなどのERRORが出たときに、その画像のpathと、どのようなエラーが出たのかを返す関数です。
    """
    if file.endswith((".tiff", ".tif")):
        erofile=[]
        lst = np.zeros(gap*8)
        xc, yc, r = MIN2(file)
        img= cv2.imread(file,cv2.IMREAD_UNCHANGED)
        for gaps in range(-gap , gap):
            #plt.clf()
            #太陽の縁を探索
            gaps_r =int(np.sqrt(np.abs(r**2 - gaps**2)))
            gaps_r = int(gaps_r)
            gaps = int(gaps)
            #  memo img[top : bottom, left : right]
            
            pl=["L","R","T","B"]
            xyof=[
                (gaps,gaps+1)
                ,[(-gaps_r-limb_wigth,-gaps_r+limb_wigth),(gaps_r-limb_wigth,gaps_r+limb_wigth)]
            ]
            #縦倒し,逆順
            pldc={
                "L":(True,0),
                "R":(True,1),
                "T":(False,0),
                "B":(False,1)
                }
            for place in pl:
                try:
                    pld = pldc[place]
                    if pld[0]:
                        y_of,x_of = xyof[0],xyof[1][pld[1]] 
                    elif not pld[0]:
                        y_of,x_of = xyof[1][pld[1]],xyof[0]
                    sample=img[int(yc+y_of[0]):int(yc+y_of[1]),int(xc+x_of[0]):int(xc+x_of[1])]
                    sample=np.array(np.ravel(sample))
                    if bool(pld[1]):
                        sample=np.flip(sample)
                    #print("sample",len(sample))
                    fd_sample = np.abs(np.gradient(sample))
                    fMaxd_sample = np.amax(fd_sample)
                    findex_Max_d_sample = np.where(fd_sample == fMaxd_sample)[0][0]
                    d_sample = np.abs(np.gradient(np.gradient(sample)))
                    Maxd_sample = np.amax(d_sample[:findex_Max_d_sample])
                    index_Max_d_sample = np.where(d_sample == Maxd_sample)[0][0]
                    index_Max_d_sample = 2*limb_wigth-index_Max_d_sample if bool(pld[1]) else index_Max_d_sample
                    real_r = gaps_r - limb_wigth +index_Max_d_sample#limbまでの距離
                    lst[gaps+(gap*(pl.index(place)*2+1))] = real_r - gaps_r
                except:
                    error_reason = str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1])
                    erofile.append((place,error_reason))
                    
                    
    return (lst ,[[file]+erofile] if erofile!=[] else "\"None\"")

def sengiri_X2(    
    file
    ,gap=170
    ,limb_wigth = 24 
    ):
    """
    ただMIN2を使うだけです。
    これはIOORが出ないと思います。
    """
    
    if file.endswith(".tiff" or ".tif"):
        lst = np.zeros(gap*8)
        xc, yc, r = MIN2(file)
        img= cv2.imread(file,cv2.IMREAD_UNCHANGED)
        for gaps in range(-gap , gap):
        
            #plt.clf()
            #太陽の縁を探索
            gaps_r =int(np.sqrt(np.abs(r**2 - gaps**2)))
            gaps_r = int(gaps_r)
            gaps = int(gaps)
            #  memo img[top : bottom, left : right]
            
            pl=["L","R","T","B"]
            xyof=[
                (gaps,gaps+1)
                ,[(-gaps_r-limb_wigth,-gaps_r+limb_wigth),(gaps_r-limb_wigth,gaps_r+limb_wigth)]
            ]
            #縦倒し,逆順
            pldc={
                "L":(True,0),
                "R":(True,1),
                "T":(False,0),
                "B":(False,1)
                }
            for place in pl:
                pld = pldc[place]
                if pld[0]:
                    y_of,x_of = xyof[0],xyof[1][pld[1]] 
                elif not pld[0]:
                    y_of,x_of = xyof[1][pld[1]],xyof[0]
                sample=img[int(yc+y_of[0]):int(yc+y_of[1]),int(xc+x_of[0]):int(xc+x_of[1])]
                sample=np.array(np.ravel(sample))
                if bool(pld[1]):
                    sample=np.flip(sample)
                print("sample",len(sample))
                fd_sample = np.abs(np.gradient(sample))
                Maxd_sample = np.amax(fd_sample)
                findex_Max_d_sample = np.where(fd_sample == Maxd_sample)[0][0]
                d_sample = np.abs(np.gradient(np.gradient(sample)))
                index_Max_d_sample = 2*limb_wigth-index_Max_d_sample if bool(pld[1]) else index_Max_d_sample
                real_r = gaps_r - limb_wigth +index_Max_d_sample#limbまでの距離
                lst[gaps+(gap*(pl.index(place)*2+1))] = real_r - gaps_r
    return lst

def sengiri_X2_justOUTside(    
    file
    ,gap=170
    ,limb_wigth = 24 
    ):
    """
    一回微分の最大値よりも中心から遠い範囲で二回微分の最大値を探すように変更しました。
    これはIOORが出ると思います。
    """
    
    if file.endswith(".tiff" or ".tif"):
        lst = np.zeros(gap*8)
        xc, yc, r = MIN2(file)
        img= cv2.imread(file,cv2.IMREAD_UNCHANGED)
        for gaps in range(-gap , gap):
        
            #plt.clf()
            #太陽の縁を探索
            gaps_r =int(np.sqrt(np.abs(r**2 - gaps**2)))
            gaps_r = int(gaps_r)
            gaps = int(gaps)
            #  memo img[top : bottom, left : right]
            
            pl=["L","R","T","B"]
            xyof=[
                (gaps,gaps+1)
                ,[(-gaps_r-limb_wigth,-gaps_r+limb_wigth),(gaps_r-limb_wigth,gaps_r+limb_wigth)]
            ]
            #縦倒し,逆順
            pldc={
                "L":(True,0),
                "R":(True,1),
                "T":(False,0),
                "B":(False,1)
                }
            for place in pl:
                try:
                    pld = pldc[place]
                    if pld[0]:
                        y_of,x_of = xyof[0],xyof[1][pld[1]] 
                    elif not pld[0]:
                        y_of,x_of = xyof[1][pld[1]],xyof[0]
                    sample=img[int(yc+y_of[0]):int(yc+y_of[1]),int(xc+x_of[0]):int(xc+x_of[1])]
                    sample=np.array(np.ravel(sample))
                    if bool(pld[1]):
                        sample=np.flip(sample)
                    print("sample",len(sample))
                    fd_sample = np.abs(np.gradient(sample))
                    Maxd_sample = np.amax(fd_sample)
                    findex_Max_d_sample = np.where(fd_sample == Maxd_sample)[0][0]
                    d_sample = np.abs(np.gradient(np.gradient(sample)))
                    d_sample=d_sample[:findex_Max_d_sample]
                    Maxd_sample=np.max(d_sample)
                    index_Max_d_sample = np.where(d_sample == Maxd_sample)[0][0]
                    index_Max_d_sample = 2*limb_wigth-index_Max_d_sample if bool(pld[1]) else index_Max_d_sample
                    real_r = gaps_r - limb_wigth +index_Max_d_sample#limbまでの距離
                    lst[gaps+(gap*(pl.index(place)*2+1))] = real_r - gaps_r
            
                except:
                    ero+=1
                    error_reason = str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1])
                    print(error_reason)
                    print("sample",sample)
                    print("indx",findex_Max_d_sample)
                    print("Msapl", Maxd_sample)
            
    return lst
def sengiri_X2_justOUTside_edgepoints(    
    file
    ,gap=170
    ,limb_wigth = 24 
    ):
    """
    listです！！説明してる暇はありません！！
    """
    twox,twoy=[],[]
    onex,oney=[],[]
    if file.endswith(".tiff" or ".tif"):
        lst = np.zeros(gap*8)
        xc, yc, r = MIN2(file)
        img= cv2.imread(file,cv2.IMREAD_UNCHANGED)
        for gaps in range(-gap , gap):
        
            #plt.clf()
            #太陽の縁を探索
            gaps_r =int(np.sqrt(np.abs(r**2 - gaps**2)))
            gaps_r = int(gaps_r)
            gaps = int(gaps)
            #  memo img[top : bottom, left : right]
            
            pl=["L","R","T","B"]
            xyof=[
                (gaps,gaps+1)
                ,[(-gaps_r-limb_wigth,-gaps_r+limb_wigth),(gaps_r-limb_wigth,gaps_r+limb_wigth)]
            ]
            #縦倒し,逆順
            pldc={
                "L":(True,0),
                "R":(True,1),
                "T":(False,0),
                "B":(False,1)
                }
            for place in pl:
                
                pld = pldc[place]
                "↑参照しておくよん"
                if pld[0]:
                    y_of,x_of = xyof[0],xyof[1][pld[1]] 
                elif not pld[0]:
                    y_of,x_of = xyof[1][pld[1]],xyof[0]
                sample=img[int(yc+y_of[0]):int(yc+y_of[1]),int(xc+x_of[0]):int(xc+x_of[1])]
                sample=np.array(np.ravel(sample))
                if bool(pld[1]):
                    sample=np.flip(sample)
                fd_sample = np.abs(np.gradient(sample))
                fMaxd_sample = np.amax(fd_sample)
                findex_Max_d_sample = np.where(fd_sample == fMaxd_sample)[0][0]
                if bool(pld[1]):
                    fd_sample=np.flip(fd_sample)
                ftruthindex_Max_d_sample = np.where(fd_sample == fMaxd_sample)[0][0]
                d_sample = np.abs(np.gradient(np.gradient(sample)))
                rowd_sample = d_sample
                d_sample=d_sample[:findex_Max_d_sample]
                Maxd_sample=np.max(d_sample)
                if bool(pld[1]):
                    rowd_sample=np.flip(rowd_sample)
                index_Max_d_sample = np.where(rowd_sample == Maxd_sample)[0][0]
                if False:
                    fig, ax = plt.subplots()
                    ax.set_title(f"{file.split('\\')[-1]}_{place}_{gaps}")
                    # sampleをプロット
                    ax.plot(sample, color="green", label="sample")
                    ax2 = ax.twinx()
                    ax.plot(fd_sample, label="fd_sample")
                    ax.plot(rowd_sample, label="d_sample")
                    ax.scatter(findex_Max_d_sample, fMaxd_sample, color="red", label="fd max")
                    ax.scatter(index_Max_d_sample, Maxd_sample, color="blue", label="d max")
                    ax.legend(loc="upper right")
                
                plt.show()
                if not bool(pld[1]):
                    index_Max_d_sample = 2*limb_wigth-index_Max_d_sample
                    ftruthindex_Max_d_sample = 2*limb_wigth-ftruthindex_Max_d_sample
                real_r = gaps_r - limb_wigth +index_Max_d_sample #limbまでの距離
                freal_r = gaps_r - limb_wigth +ftruthindex_Max_d_sample#limbまでの距離
                if place == "L":
                    twox.append(xc-real_r)
                    twoy.append(yc+gaps)
                    onex.append(xc+-freal_r)
                    oney.append(yc+gaps)
                elif place == "R":
                    twox.append(xc+real_r)
                    twoy.append(yc+gaps)
                    onex.append(xc+freal_r)
                    oney.append(yc+gaps)
                elif place == "T":
                    twox.append(xc+gaps)
                    twoy.append(yc-real_r)
                    onex.append(xc+gaps)
                    oney.append(yc-freal_r)
                elif place == "B":
                    twox.append(xc+gaps)
                    twoy.append(yc+real_r)
                    onex.append(xc+gaps)
                    oney.append(yc+freal_r)
    return [twox,twoy],[onex,oney]

    return twox,twoy
def sengiri_X2_drowero(file,
                    lookgap=None,
                    gap=170,
                    limb_wigth = 24):
    """
    IOORなどERRORが出たときに、どのようなサンプルが得られているのかを確認するための関数です。
    lookgap:EROORが出なくても指定されたgapのときのサンプルをプロットします。default:None
    """
    
    if file.endswith(".tiff" or ".tif"):
        erofile=[]
        lst = np.zeros(gap*8)
        xc, yc, r = MIN2(file,look=False)
        img= cv2.imread(file,cv2.IMREAD_UNCHANGED)
        for gaps in range(-gap , gap):
        
            #plt.clf()
            #太陽の縁を探索
            gaps_r =int(np.sqrt(np.abs(r**2 - gaps**2)))
            gaps_r = int(gaps_r)
            gaps = int(gaps)
            #  memo img[top : bottom, left : right]
            
            pl=["L","R","T","B"]
            xyof=[
                (gaps,gaps+1)
                ,[(-gaps_r-limb_wigth,-gaps_r+limb_wigth),(gaps_r-limb_wigth,gaps_r+limb_wigth)]
            ]
            #縦倒し,逆順
            pldc={
                "L":(True,0),
                "R":(True,1),
                "T":(False,0),
                "B":(False,1)
                }
            for place in pl:
                try:
                    pld = pldc[place]
                    if pld[0]:
                        y_of,x_of = xyof[0],xyof[1][pld[1]] 
                    elif not pld[0]:
                        y_of,x_of = xyof[1][pld[1]],xyof[0]
                    sample=img[int(yc+y_of[0]):int(yc+y_of[1]),int(xc+x_of[0]):int(xc+x_of[1])]
                    sample=np.array(np.ravel(sample))
                    if bool(pld[1]):
                        sample=np.flip(sample)
                    #print("sample",len(sample))
                    fd_sample = np.abs(np.gradient(sample))
                    fMaxd_sample = np.amax(fd_sample)
                    findex_Max_d_sample = np.where(fd_sample == fMaxd_sample)[0][0]
                    d_sample = np.abs(np.gradient(np.gradient(sample)))
                    Maxd_sample = np.amax(d_sample[:findex_Max_d_sample])
                    index_Max_d_sample = np.where(d_sample == Maxd_sample)[0][0]
                    index_Max_d_sample = 2*limb_wigth-index_Max_d_sample if bool(pld[1]) else index_Max_d_sample
                    real_r = gaps_r - limb_wigth +index_Max_d_sample#limbまでの距離
                    lst[gaps+(gap*(pl.index(place)*2+1))] = real_r - gaps_r
                    if gaps==lookgap:    
                        fig, ax = plt.subplots()
                        # タイトル
                        fig.suptitle(f"{file.split('\\')[-1]}_{place}_{gaps}")
                        fig.text(0.5, 0.92, f"error reason: {str(sys.exc_info()[0]) + ': ' + str(sys.exc_info()[1])}", ha='center')
                        # 第1軸（左）
                        ax.plot(fd_sample, label="fd_sample")
                        ax.plot(d_sample, label="d_sample")
                        ax.scatter(findex_Max_d_sample, fMaxd_sample, color="red")
                        # 第2軸（右）
                        ax2 = ax.twinx()
                        ax2.plot(sample, color="green", label="sample")
                        #min2の縁をプロット
                        ax2.axvline(x=limb_wigth, color="gray", label="min2 edge", linestyle="--")
                        # 凡例をまとめる
                        lines1, labels1 = ax.get_legend_handles_labels()
                        lines2, labels2 = ax2.get_legend_handles_labels()
                        ax.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

                        erofile.append(file)
                        plt.show(block=True)
                    
                except:
                    error_reason = str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1])
                    
                    fig, ax = plt.subplots()
                    # タイトル
                    fig.suptitle(f"{file.split('\\')[-1]}_{place}_{gaps}")
                    fig.text(0.5, 0.92, f"error reason: {str(sys.exc_info()[0]) + ': ' + str(sys.exc_info()[1])}", ha='center')
                    # 第1軸（左）
                    ax.plot(fd_sample, label="fd_sample")
                    ax.plot(d_sample, label="d_sample")
                    ax.scatter(findex_Max_d_sample, fMaxd_sample, color="red")
                    # 第2軸（右）
                    ax2 = ax.twinx()
                    ax2.plot(sample, color="green", label="sample")
                    #min2の縁をプロット
                    ax2.axvline(x=limb_wigth, color="gray", label="min2 edge", linestyle="--")
                    # 凡例をまとめる
                    lines1, labels1 = ax.get_legend_handles_labels()
                    lines2, labels2 = ax2.get_legend_handles_labels()
                    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

                    erofile.append(file)
                    plt.show(block=True)
                    
    return lst