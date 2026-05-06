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
from KANSUU import folder_read
from KANSUU import llen
from kansu_module import Kansu_onlystd
from sengiries import sengiri_X2_justOUTside

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
                result=Kansu_onlystd(patt,ex,sengiri_X2_justOUTside)#主処理、フォルダのパスと並列処理のやつが引数。

            
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