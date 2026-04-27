#-- ライブラリのインポート --
#画像を読み込み、円を検出するライブラリ
import cv2
#数学の計算をするライブラリ
import numpy as np
#プロットするライブラリ
import matplotlib.pyplot as plt
#ファイルのリストを作るライブラリ
import os
import shutil
#csvファイルの読み出しをするライブラリ
import pandas as pd

#並列処理のライブラリ(あいばら追加)
import concurrent.futures
#進行度合いをだすやつ(あいばら追加)
import tqdm
import datetime
import time
from pathlib import Path
import glob
import time
from tkinter import filedialog as fd
from scipy.interpolate import CubicSpline
from scipy.optimize import minimize_scalar
from win11toast import toast
import sys
#20260206
argv=sys.argv
a1 = sys.argv[1]
a2=int(sys.argv[2])

#実行とデバックにて走らせてください
pats=a1
ind=a2
outdir=r"C:\Users\fujit\OneDrive\デスクトップ\allfram"
#outdir=r"C:\Users\fujit\OneDrive\デスクトップ\allfram"

gap = 170
limb_wigth = 48 #単位はpix
limb_wigth = int(limb_wigth / 2)
pad = 5

houghC_param1=30
houghC_param2=100
houghTF=True


start=time.time()
def folder_read(fpath):
    folders = [
        name for name in os.listdir(fpath)
        if os.path.isdir(os.path.join(fpath, name))
        ]
    return folders
def sengiri(file):
    lst = np.empty(gap*8)
    #plt.clf()
    #保存するファイル名
    #file0=file
    #読み込むファイル名
    #-- ファイルの読み込み 読み込んだ太陽像はimg--
    img=cv2.imread(file,0)
    #-- 太陽像を円と考えて検出する --
    #（※太陽像の真ん中がサチレーションしているので、うまく検出できていない：宿題）
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, dp=3,minDist=80,param1=houghC_param1,param2=houghC_param2, minRadius=0, maxRadius=0)
    if circles is None:
        houghTF=False
        return None
    circles = np.array(circles)
    #-- 検出された円の中心(xc,yc)と円の半径r --
    xc=np.int64(circles[0,0,0])
    yc=np.int64(circles[0,0,1])
    r=np.int64(circles[0,0,2])
    #print(r)
    if file.endswith(".tiff" or ".tif"):
        img=cv2.imread(file,-1)

    #太陽像を数字として扱うための設定
    img=np.float64(img)
    imgg= cv2.imread(file,0)


    #プロットの消去
    #plt.clf()
    #-- 空間微分によるlimb位置の検出 --
    #  memo img[top : bottom, left : right]
    #右limbを一次元(一本線)で切り出し
    #plt.imshow(img,cmap='gray')
    pix_dis = 1000
    x = np.array(range(limb_wigth*2))
    #x_dense = np.linspace(0,limb_wigth*2-1, limb_wigth*2*pix_dis)
    for gaps in range(-gap , gap):
        #plt.clf()
        #太陽の縁を探索
        gaps_r =int(np.sqrt(np.abs(r**2 - gaps**2)))
        #  memo img[top : bottom, left : right]
        #これは左縁
        sample = img[yc+gaps:yc+gaps+1,xc-gaps_r-limb_wigth:xc-gaps_r+limb_wigth]
        sample = np.ravel(sample)
        d_sample = np.abs(np.gradient(sample))
        Maxd_sample = np.amax(d_sample)
        index_Max_d_sample = np.where(d_sample == Maxd_sample)[0][0]
        start = max(index_Max_d_sample - pad, 0)
        end = min(index_Max_d_sample + pad, len(sample)-1)
        x2 = np.arange(start, end)
        y2 = sample[start:end]
        #cs = CubicSpline(x2, y2)
        #cs_g = cs.derivative()
        #max_x = minimize_scalar(lambda t: -cs_g(t), bounds=(x2[0], x2[-1]), method='bounded')
        real_r = gaps_r - limb_wigth + index_Max_d_sample#limbまでの距離 index_Max_d_sampleをx2.xに変えると補完*4
        lst[gaps+gap] = real_r - gaps_r
        
        #plt.plot([xc-gaps_r-limb_wigth,xc-gaps_r+limb_wigth],[yc+gaps,yc+gaps],color="b")

        #繰り返し
        #右縁
        sample=img[yc+gaps:yc+gaps+1,xc+gaps_r-limb_wigth:xc+gaps_r+limb_wigth]
        sample = np.ravel(sample)
        d_sample = np.abs(np.gradient(sample))
        Maxd_sample = np.amax(d_sample)
        index_Max_d_sample = np.where(d_sample == Maxd_sample)[0][0]
        start = max(index_Max_d_sample - pad, 0)
        end = min(index_Max_d_sample + pad, len(sample)-1)
        x2 = np.arange(start, end)
        y2 = sample[start:end]
        #cs = CubicSpline(x2, y2)
        #cs_g = cs.derivative()
        #max_x = minimize_scalar(lambda t: cs_g(t), bounds=(x2[0], x2[-1]), method='bounded')        
        real_r = gaps_r - limb_wigth +index_Max_d_sample#limbまでの距離
        lst[gaps+(gap*3)] = real_r - gaps_r

        #plt.plot([xc+gaps_r-limb_wigth,xc+gaps_r+limb_wigth],[yc+gaps,yc+gaps],color="b")
        #上縁
        sample=img[yc-gaps_r-limb_wigth:yc-gaps_r+limb_wigth,xc+gaps:xc+gaps+1]
        sample = np.ravel(sample)
        d_sample = np.abs(np.gradient(sample))
        Maxd_sample = np.amax(d_sample)
        index_Max_d_sample = np.where(d_sample == Maxd_sample)[0][0]
        start = max(index_Max_d_sample - pad, 0)
        end = min(index_Max_d_sample + pad, len(sample)-1)
        x2 = np.arange(start, end)
        y2 = sample[start:end]
        #cs = CubicSpline(x2, y2)
        #cs_g = cs.derivative()
        #max_x = minimize_scalar(lambda t: -cs_g(t), bounds=(x2[0], x2[-1]), method='bounded')
        real_r = gaps_r - limb_wigth + index_Max_d_sample#limbまでの距離
        lst[gaps+(gap*5)] = real_r - gaps_r

        #plt.plot([xc+gaps,xc+gaps],[yc-gaps_r-limb_wigth,yc-gaps_r+limb_wigth],color="r")
        #下縁
        sample=img[yc+gaps_r-limb_wigth:yc+gaps_r+limb_wigth,xc+gaps:xc+gaps+1]
        sample = np.ravel(sample)
        d_sample = np.abs(np.gradient(sample))
        Maxd_sample = np.amax(d_sample)
        index_Max_d_sample = np.where(d_sample == Maxd_sample)[0][0]
        start = max(index_Max_d_sample - pad, 0)
        end = min(index_Max_d_sample + pad, len(sample)-1)
        x2 = np.arange(start, end)
        y2 = sample[start:end]
        #cs = CubicSpline(x2, y2)
        #cs_g = cs.derivative()
        #max_x = minimize_scalar(lambda t: cs_g(t), bounds=(x2[0], x2[-1]), method='bounded')
        real_r = gaps_r - limb_wigth + index_Max_d_sample#limbまでの距離

        lst[gaps+(gap*7)] = real_r - gaps_r

    return lst
def Kansu(Sam_dir,executor=None):
    foldername = os.path.basename(os.path.dirname(Sam_dir))
    #print()
    #print("fname",foldername)
    if "LT" in foldername :
        location = "LoofTop"
    elif "PL" in foldername :
        location = "PoolSide"
    else:
        location = "Unknown"
    #Bunsan_Alltime = 0
    #lstはシーイングサイズを格納
    lst = []
    #sizeは太陽のサイズ（半径）を格納するリスト
    files = glob.glob(Sam_dir+"\\*.tiff") + glob.glob(Sam_dir+"\\*.tif") + glob.glob(Sam_dir+"\\*.jpg")
    #print("filesssss",files)
    with tqdm.tqdm(total=len(files)) as progress:
        lsts=ex.map(sengiri, files)
        for data in lsts:
            progress.update(1)
            lst.append(data)


    st_max = 0
    st_min = 1000000000
    counter = 0  
    mxcount = 0
    mncount = 0
    #各フレームの標準偏差をstsに格納
    sts = []
    for l in lst:
        if l is None:
            continue
        st = np.std(l)
        sts.append(float(st))
        if st_max < st:
            st_max = st
        if st_min > st:
            st_min = st
        counter += 1
    
    #print("MAX",st_max,"frame",mxcount)
    #print("MIN",st_min,"frame",mncount)
    print("median",np.median(sts))
    print("average",np.average(sts))
    #print("size",np.average(sizes))
    #print("location",location)
    return sts
def llen(ist):
    return range(len((ist)))
def make_sheet(result,outpath,mode,nc):
    colmsnumber=0
    colms=[]
    data=[]
    
    if mode=="a": 
        df = pd.read_excel(outpath)
        colms = df.columns.tolist()   # 列名のリスト
        data = df.values.tolist()       #データのリスト
    else:
        colms = []
        data=[]
    colmsnumber=len(colms)
    colms.append(nc)
    if len(data)>len(result):
        for i in range(len(data)-len(result)):
            result.append(None)
    for re in llen(result):
        if len(data)<=re:
            data.append([])
        for i in range(colmsnumber-len(data[re])):
            data[re].append(None)
        data[re].append(result[re])
        
    return data,colms   
if __name__=="__main__":#関数の呼び出し時は起動しない
    foldist=folder_read(pats)
    #print("foldist",foldist)
    if foldist==[]:
        foldist=[pats]
    #もしpats内にディレクトリがなければpats内の画像を処理するものと解釈
    for i in foldist:
        print("I DO",foldist.index(i),"/in",len(foldist))
        try:
            if pats != i:#pats内にディレクトリがない場合に困るから条件分岐
                patt=pats+"\\"+(i)
                out_path=outdir+"\\"+pats.split("\\")[ind]+"_by_"+__file__.split("\\")[-1]+".xlsx"#出力xlsxのパスを作成
            else:
                patt=pats
                out_path=outdir+"\\"+pats.split("\\")[-1]+"_by_"+__file__.split("\\")[-1]+".xlsx"#出力xlsxのパスを作成
            with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
                #↑並列処理用のやつ
                result=Kansu(patt,ex)#主処理、フォルダのパスと並列処理のやつが引数。

            
            mode="a" if os.path.exists(out_path) else "w"#出力xlsxが既存か否かによってmake_sheetのmodeを変更
            data,colms=make_sheet(result,out_path,mode,nc=i)#xlsxのデータを作成
            df = pd.DataFrame(data, columns=colms)#書き込み用のやつ
            df.to_excel(out_path, index=False)#書き込み

            toast("Python通知", f"{i}が終了しました\nfrom {__file__.split("\\")[-1]}")
            print(patt)
            print(out_path)
        except:
            if not houghTF :
                error_reason="HOUGH"
            else:
                error_reason="UNKNOWN"
            toast("Python通知",f"ERROR\nwhy error{error_reason}\nfrom {__file__.split("\\")[-1]}")
    toast("Python通知",f"{pats}の処理がすべて終了しました。\nfrom {__file__.split("\\")[-1]}")
    print("time:",start-time.time())