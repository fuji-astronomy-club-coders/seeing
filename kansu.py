import os
import glob
import numpy as np
import cv2
import tqdm

def Kansu(Sam_dir,ex,anysengiri):
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
        lsts=ex.map(anysengiri, files)
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