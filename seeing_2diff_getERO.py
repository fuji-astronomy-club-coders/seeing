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
from KANSUU import make_sheet
from KANSUU import place
from KANSUU import list_folders
from KANSUU import MIN2
from kansu_module import Kansu
from sengiries import sengiri_X2_GetERO


argv=sys.argv

#a1 = argv[1] if len(argv) > 1 else fd.askdirectory(title="処理するフォルダを選択してください")
a1=r"J:\2025-08-30Z\2025-08-30-LT"
a2=-1
#実行とデバックにて走らせてください
pats=a1
outdir=r"C:\Users\fujit\OneDrive\デスクトップ\resultまとめ"
#outdir=r"C:\Users\fujit\OneDrive\デスクトップ\allfram"

gap = 170
limb_wigth = 24 #単位はpix
limb_wigth =int(limb_wigth / 2)
pad = 5
count=0
dif2=False
start=time.time()

    

if __name__=="__main__":#関数の呼び出し時は起動しない
    plac=place(a1.split("\\")[-1])
    sht=""
    for i in a1.split("\\")[-1].split("-")[1:]:
        sht+=i
    foldist=list_folders(pats)
    resultret=[]
    colm=[]
    #print("foldist",foldist)
    if foldist==[]:
        foldist=[pats]
    resultrt=[]
    resulter=[]
    colmre=[]
    colmer=[]
    #もしpats内にディレクトリがなければpats内の画像を処理するものと解釈
    for i in foldist:
        
        print("I DO",foldist.index(i),"/in",len(foldist))
        if pats != i:#pats内にディレクトリがない場合に困るから条件分岐
            patt=pats+"\\"+(i)
            out_path=outdir+"\\"+pats.split("\\")[-1]+"_by_"+__file__.split("\\")[-1]+".xlsx"#出力xlsxのパスを作成
        else:
            patt=pats
            out_path=outdir+"\\"+pats.split("\\")[-1]+"_by_"+__file__.split("\\")[-1]+".xlsx"#出力xlsxのパスを作成
        with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as ex:
            #↑並列処理用のやつ
            result,erofile=Kansu(patt,ex,sengiri_X2_GetERO)#主処理、フォルダのパスと並列処理のやつが引数。
            erofile=erofile[0] if len(erofile)>0 else ["None"]
            colmre.append([plac+"."+str(foldist.index(i)),i])
            colmer.append([plac+"."+str(foldist.index(i)),"ERO" if any(x != "None" for x in erofile) else "NoneERO"])
            
            toast("Python通知", f"{i}が終了しました\nfrom {__file__.split("\\")[-1]}")
        resultrt.append(result)
        resulter.append(erofile)
        resultret=resultrt+resulter
    colm=colmre+colmer
    parent=["seeing","erofiles"]
    paren=len(colmre)
    outdir=os.path.join(outdir,f"HIKISUUkensyou_seev2-outsideNoter-Kensyoyu_by_{__file__.split('\\')[-1]}.xlsx")
    print(colm)
    make_sheet(
            resultret,
            colm,
            outdir,
            parent=parent,
            panum=[paren],
            pareenp=True,
            polycolm=True,
            cel_sheet=sht,
            recode_when=True
        )
    toast("Python通知",f"{pats}の処理がすべて終了しました。\nfrom {__file__.split("\\")[-1]}")
    print("time:",start-time.time())