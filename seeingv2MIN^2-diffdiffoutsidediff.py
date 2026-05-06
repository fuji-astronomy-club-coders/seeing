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
import sys
from win11toast import toast
from KANSUU import MIN2


argv=sys.argv

a1 = r"J:\2025-08-30Z\2025-08-30-PL"
a2=-1
#実行とデバックにて走らせてください
pats=a1
ind=a2
outdir=r"C:\Users\fujit\OneDrive\デスクトップ"
#outdir=r"C:\Users\fujit\OneDrive\デスクトップ\allfram"

gap = 170
limb_wigth = 48 #単位はpix
limb_wigth =int(limb_wigth / 2)
pad = 5
count=0





start=time.time()
def folder_read(fpath):
    folders = [
        name for name in os.listdir(fpath)
        if os.path.isdir(os.path.join(fpath, name))
        ]
    return folders

def sengiri_X2_justOUTside(file):
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
    files = glob.glob(Sam_dir+"\\"+"*.tiff") + glob.glob(Sam_dir+"*.tif") + glob.glob(Sam_dir+"*.jpg")
    #print("files",files)
    with tqdm.tqdm(total=len(files)) as progress:
        lsts=ex.map(sengiri_X2_justOUTside, files)
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
            error_reason = str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1])
            print(error_reason)
            toast("Python通知",f"ERROR\nwhy error{error_reason}\nfrom {__file__.split("\\")[-1]}")
    toast("Python通知",f"{pats}の処理がすべて終了しました。\nfrom {__file__.split("\\")[-1]}")
    print("time:",start-time.time())