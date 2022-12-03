


import numpy as np
import cv2 as cv

#load image
image = cv.imread("C:/Users/busra/BIL561/HW8/test7.jpg",0)
"""
def CLAHE(image, blocks, threshold):
    (m, n) = image.shape
    block_m = int(m / blocks)
    block_n = int(n / blocks)
    maps = []
    for i in range(blocks):
            row_maps = []
            for j in range(blocks):
                # block border
                si, ei = i * block_m, (i + 1) * block_m
                sj, ej = j * block_n, (j + 1) * block_n
                    
                # block image array
                block_img_arr = image[si : ei, sj : ej]
                            
                
                row_maps.append(block_img_arr)
            maps.append(row_maps)
    
    for map in maps:
        hist,bins=np.histogram(image.flatten(),256,[0,256])
        cdf=hist.cumsum()
        cdf_normalised=cdf*hist.max()/cdf.max()
        cdf_m=np.ma.masked_equal(cdf,0)
        cdf_o=(cdf_m-cdf_m.min())*255/(cdf_m.max()-cdf_m.min())
        cdff=np.ma.filled(cdf_o,0).astype('uint8')
        image2=cdff[image]

inputs:
tile_size= 8,16,32
histogram hesapla, hangi pikselden kaÃ§ tane var
AHE da; her tile'da bu histogram hesaplanÄ±r.Ama uniform yere denk gelirsek histogram peak yapar
Cdf alÄ±nÄ±r. threshold belirlenir. Th Ã¼stÃ¼ndeki pikselleri random altta kaalan piksel alanÄ±na dagÄ±t
replicate padding kullan

resmi kutucuklara bÃ¶l
histogram bul, cdf hesapla, normalize et. Bu pikselin lookup'Ä±nÄ± bul
diÄŸer tile'larÄ±n da merkez piksellerinin konumunu ve lookuplarÄ± bulunur.
piksel degeri ara noktaya denk geldiÄŸinde yakÄ±n pikseller seÃ§ilir,interpolasyon yapÄ±lÄ±r. Hangi piksele en yakÄ±nsa v1,v2,v3,v4 
"""
     
def CLAHE(image, tile_size, thr):
   
    w,h = image.shape
    tile_weight = w // tile_size
    tile_height = h // tile_size
        
    # splitting boxes of image
    output = []
    for i in range(tile_size):
        r_output = []
        for j in range(tile_size):
              
            # tile image
            tile_image = image[i * tile_weight : (i + 1) * tile_weight, j * tile_height : (j + 1) * tile_height]
                
            # calculate histogram of tiles
            hist,bins=np.histogram(tile_image.flatten(),256,[0,256])
            
            # thresholding tiles
            sums = sum(hist)
            threshold = sums / len(hist) * thr
            total = sum([h - threshold for h in hist if h >= threshold])
            mean = total / len(hist)
        
            all_hists = [0 for _ in hist]
            for i in range(len(hist)):
                if hist[i] >= threshold:
                    all_hists[i] = int(threshold + mean)
                else:
                    all_hists[i] = int(hist[i] + mean)
            
            #cdf tiles
            cdf = ((255 / (tile_weight * tile_height)) * (np.cumsum(np.array(all_hists)))).astype("uint8")
            
            # save
            r_output.append(cdf)
        output.append(r_output)

    #make perfect clahe for broder values
    arr = image.copy()
    for i in range(w):
        for j in range(h):
            r = int((i - tile_weight / 2) / tile_weight)      # the row index of the left-up mapping function
            c = int((j - tile_height / 2) / tile_height)      # the col index of the left-up mapping function
                
            x1 = (i - (r + 0.5) * tile_weight) / tile_weight  # the x-axis distance to the left-up mapping center
            y1 = (j - (c + 0.5) * tile_height) / tile_height  # the y-axis distance to the left-up mapping center
                
            lu = 0    # mapping value of the left up cdf
            lb = 0    # left bottom
            ru = 0    # right up
            rb = 0    # right bottom
                
            # four corners use the nearest mapping directly
            if r < 0 and c < 0:
                arr[i][j] = output[r + 1][c + 1][image[i][j]]
            elif r < 0 and c >= tile_size - 1:
                arr[i][j] = output[r + 1][c][image[i][j]]
            elif r >= tile_size - 1 and c < 0:
                arr[i][j] = output[r][c + 1][image[i][j]]
            elif r >= tile_size - 1 and c >= tile_size - 1:
                arr[i][j] = output[r][c][image[i][j]]

            # four border case using the nearest two mapping : linear interpolate
            elif r < 0 or r >= tile_size - 1:
                if r < 0:
                    r = 0
                elif r > tile_size - 1:
                    r = tile_size - 1
                left = output[r][c][image[i][j]]
                right = output[r][c + 1][image[i][j]]
                arr[i][j] = (1 - y1) * left + y1 * right
            elif c < 0 or c >= tile_size - 1:
                if c < 0:
                    c = 0
                elif c > tile_size - 1:
                    c = tile_size - 1
                up = output[r][c][image[i][j]]
                bottom = output[r + 1][c][image[i][j]]
                arr[i][j] = (1 - x1) * up + x1 * bottom
                
            # bilinear interpolate for inner pixels
            else:
                lu = output[r][c][image[i][j]]
                lb = output[r + 1][c][image[i][j]]
                ru = output[r][c + 1][image[i][j]]
                rb = output[r + 1][c + 1][image[i][j]]
                arr[i][j] = (1 - y1) * ( (1 - x1) * lu + x1 * lb) + y1 * ( (1 - x1) * ru + x1 * rb)
    arr = arr.astype("uint8")
    return arr


# CLAHE
clahe_image=CLAHE(image,16,4)

#opencv Clahe
clahe = cv.createCLAHE(clipLimit=4, tileGridSize=(16,16))
cl1 = clahe.apply(image)
hist_out=equ = cv.equalizeHist(image)

cv.imshow("clahe", clahe_image)
cv.imshow("cv2 clahe", cl1)
cv.imshow("histogram out",hist_out)


cv.waitKey(0)
cv.destroyAllWindows()