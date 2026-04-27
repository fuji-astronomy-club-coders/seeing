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
from tkinter import filedialog as fd
from scipy.interpolate import CubicSpline
from scipy.optimize import minimize_scalar
#実行とデバックにて走らせてください

#20260106
patt=r"J:\2025-08-30Z\2025-08-30-LT\2025-08-30-0448_4-CapObj"
Vdir =patt.split(":")[0]+":"
V_folderName=patt.split(":")[1]
dir0= "J:\\"
dir=dir0+'img\\'
dirr = dir0 + "result\\"
sdir1=dir0+'simg\\'
sdir2=dir0+'sprof\\'
sdir3=dir0+"3d\\"
scsv=dir0+"position.csv"
#V_dirs  = glob.glob(Vdir+V_folderName +"\\"+ "*\\")
V_dirs  = glob.glob(Vdir+V_folderName + "*\\")
results = []
sizes = []
gap = 170
JUNSUIGaps=[]
limb_wigth = 48 #単位はpix
limb_wigth = int(limb_wigth / 2)
pad = 5
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
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, dp=3,minDist=80,param1=30,param2=100, minRadius=0, maxRadius=0)
    if circles is None:
        return None
    circles = np.array(circles)
    #-- 検出された円の中心(xc,yc)と円の半径r --
    xc=np.int64(circles[0,0,0])
    yc=np.int64(circles[0,0,1])
    r=np.int64(circles[0,0,2])
    print(r)
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
        
        """
        print(y_max,position[0]/pix_dis)
        plt.plot(x, sample, 'o', label='Original Data')
        plt.plot(x_dense, cs(x_dense), label='Cubic Spline')
        plt.plot(x_dense, cs_g(x_dense), label='Cubic Spline_gradiented')
        plt.plot(max_x.x, cs(max_x.x), 'rx', label='Maximum')

        #plt.plot(x_dense, poly_lagrange(x_dense), label='Lagrange Polynomial')
        #plt.plot(x_dense, poly_fit(x_dense), label='2nd Degree Fit')
        plt.legend()
        plt.grid()
        plt.show()
        exit()
        """     
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
    #print(foldername)
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
    sizes = []
    files = glob.glob(Sam_dir+"*.tiff") + glob.glob(Sam_dir+"*.tif") + glob.glob(Sam_dir+"*.jpg")

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
            mxcount= counter
        if st_min > st:
            st_min = st
            mncount=counter
        counter += 1
    print(sts)
    Sts=sts
    #print("MAX",st_max,"frame",mxcount)
    #print("MIN",st_min,"frame",mncount)
    print("median",np.median(sts))
    print("average",np.average(sts))
    #print("size",np.average(sizes))
    #print("location",location)
    """
    plt.xlim(0,1000)
    plt.ylim(0, 9)
    plt.grid(True)

    plt.scatter(range(len(sts)),sts,color = "#003CFF",s=5)
    plt.savefig(dirr + foldername + "sanpuNew.png")
    """
    x = []
    for i in range(len(sts)):
        x.append(i)
    
    #ここは移動平均
    """
    n_conv = 10
    b = np.ones(n_conv)/n_conv 
    sts1 = np.convolve(sts, b , mode="same")
    sts1mx=0
    sts1mn=9999999
    sts1counter = 0  
    sts1mxcount = 0
    sts1mncount = 0
    for i in range(10,len(sts1)-10):
        if sts1mx < i:
            sts1mx = i
            sts1mxcount= counter
        if sts1mn > i:
            sts1mn = i
            sts1mncount=counter
        counter += 1
    fig=plt.figure(figsize=(15,5))
    ax=fig.add_subplot(111)
    ax.plot(x[100:130],sts[100:130],color="#E05BB4B0",lw = 10)
    sts1[0:9]=0
    sts1[len(sts1)-10:len(sts1)]=0
    ax.plot(x[100:130],sts1[100:130],"--",color="#BB039C",lw = 7)
    ax.set_title(foldername)
    #ax.set_xlabel("frame")
    #ax.set_ylabel("standard deviation")"
    if not os.path.isdir(dirr+"averages"+"\\"):
        os.makedirs(dirr+"averages"+"\\")
    plt.savefig(dirr+"averages"+"\\"+foldername+".png")
    #ここまでが移動平均
    """
    lst = np.array([V_folderName + foldername,st_max,mxcount,st_min,mncount,datetime.datetime.now().replace(microsecond=0),np.median(sts),np.average(sts),location])#sts1mx,sts1mn])
    lst = lst.reshape(len(lst),1)
    #この行でエラーが出る場合はプログラムフォルダ内に「result」フォルダを作成し、「results.xlsx」を作成してください。
    df = pd.DataFrame(lst.T, columns=["name", "max", "max_frame", "min", "min_frame","Date time","median","average","location"])#,"移動平均mx","移動平均mn"])
    return df,Sts
ja=0

if __name__ == '__main__':
    Df=pd.DataFrame()
    with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
        for i in V_dirs:
            print(os.path.basename(os.path.dirname(i)))
            add = Kansu(i,ex)[0]
            Df = pd.concat([Df,add])
            #print()
            #plt.close
            #Df.to_csv(dirr+V_folderName+"result"+".csv", index=False,)
            Df.to_csv("C:\\Users\\fujit\\OneDrive\\デスクトップ\\cop_gaps_seev2.csv", index=False,)
            JUNSUIGaps+=Kansu(i,ex)[1]
            
        ja=1


import csv
print('JUNSUI',JUNSUIGaps,'JUNSI')
name=V_folderName.split("\\")
name=name[-2]+"_"+name[-1]+".csv"
if ja==1:
    with open("C:\\Users\\fujit\\OneDrive\\デスクトップ\\allframeseeiingbyhahu\\"+name,mode='w') as fe:
            file=csv.writer(fe)
            file.writerow(JUNSUIGaps)
    print(f"CSVファイル  にデータを書き出しました。")
    
print(patt)