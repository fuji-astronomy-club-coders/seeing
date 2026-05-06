import numpy as np
import matplotlib.pyplot as plt
import cv2
import re
import sys
import os
import tqdm
from KANSUU import MIN2 
from sengiries import sengiri_X2_drowero
gap=170
limb_wigth = 90 #単位はpix
limb_wigth =int(limb_wigth / 2)


inputdir=r"j:\2025-08-30Z\2025-08-30-LT"
import KANSUU
siteisub=True
if siteisub:
    foldist=KANSUU.list_folders(inputdir)
else:
    foldist=[r"J:\2025-08-30Z\2025-08-30-LT\2025-08-30-0437_9-CapObj"]
for fold in KANSUU.llen(foldist):
    foldpath=os.path.join(inputdir,foldist[fold])
    files=KANSUU.list_files(foldpath)
    totalfiles=len(files)
    nowfiles=0
    for file in files:
        nowfiles += 1
        filepath=os.path.join(foldpath,file)
        if file.endswith((".tiff", ".tif")):
            resu = sengiri_X2_drowero(filepath)
            print(file, " std:", np.std(resu),f"{nowfiles}/{totalfiles}")
