import cv2
import numpy as np
import matplotlib.pyplot as plt
from sengiries import sengiri_X2_justOUTside_edgepoints

sun_image=r"J:\2025-08-30Z\2025-08-30-PL\2025-08-30-0441_9-CapObj\img00000001.tiff"

two,one=sengiri_X2_justOUTside_edgepoints(sun_image)
plt.imshow(cv2.imread(sun_image, cv2.IMREAD_UNCHANGED), cmap='gray')
size=25
plt.scatter(two[0], two[1], color='cyan', label='twice diff max', s=size)
plt.scatter(one[0], one[1], color='magenta', label='first diff max', s=size)
plt.legend()    
plt.show()
print ("data:", sun_image)