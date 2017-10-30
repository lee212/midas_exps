import numpy as np
from skbeam.core.accumulators.binned_statistic import RPhiBinnedStatistic
from skbeam.core.utils import angle_grid, radial_grid
from skbeam.core.image import construct_rphi_avg_image
import os
import datetime
import time

def reconstruct_nfold(img, sym, polar_shape, mask=None, origin=None):
    ''' 
    Reconstruct an image assuming a certain symmetry.
        
    Parameters
    ----------
    img : the image
            
    sym : the symmetry of the sample
            
    polar_shape : the shape of the new polar coordinate image
        
    Returns
    -------
    reconstructed_image : the reconstructed  image   
    '''
    shape = 0
    shape = img.shape
    rphibinstat = RPhiBinnedStatistic(shape, bins=polar_shape, mask=mask, origin=origin)
    angles = rphibinstat.bin_centers[1]
    radii = rphibinstat.bin_centers[0]
    rphi_img = rphibinstat(img)
    # create mask from np.nans since RPhiBinnedStatistic fills masked regions with np.nans
    rphimask = np.ones_like(rphi_img)
    rphimask[np.where(np.isnan(rphi_img))] = 0

    reconstructed_image = np.zeros_like(img)
    reconstructed_image_mask = np.zeros_like(img,dtype=int)
    # symmetry
    dphi = 2*np.pi/float(sym)
    for i in range(sym):
        anglesp = angles + dphi*i
        imgtmp = construct_rphi_avg_image(radii, anglesp, rphi_img,
                                              shape=shape, center=origin, mask=rphimask)
        w = np.where(~np.isnan(imgtmp))
        reconstructed_image[w] += imgtmp[w]
        reconstructed_image_mask += (~np.isnan(imgtmp)).astype(int)
            
    # the mask keeps count of included pixels. Average by this amount
    try:
        reconstructed_image /= reconstructed_image_mask
    except Exception as e:
        print  'Division failed at line 50' , reconstructed_image_mask
        pass 
    
    return reconstructed_image




run_timestamp=datetime.datetime.now()
RESULT_FILE= "results/batch-construct_phi-" + run_timestamp.strftime("%Y%m%d-%H%M%S") + ".csv"

try:
    os.makedirs('results')
except:
    pass

output_file = open(RESULT_FILE, "a")
output_file.write("Image_Dimensions,Image_size(MB),TTC\n")


## Generate the image
# first generate some random scattering pattern
# There are missing regions

dims = 400  # 1 MB
dims = 600   #2 MB
dims = 800   #4MB
dims = 1050 # 8MB
dims = 1450 # 16 MB
dims = 2050 #32 MB
dims = 2900  # 64 MB
dims = 4100   # 128 MB
dims = 5800   # 256 MB


pixel_sizes = [400,600,800,1050,1450,2050,2900,4100,5800]
# 1MB, 2MB, 4MB, 8MB, 16MB, 32MB, 64MB, 128MB, 256MB
for pixels in pixel_sizes:

    shape = pixels, pixels
    x0,y0 = 401, 401
    ANGLES = angle_grid((y0, x0), shape)
    RADII = radial_grid((y0, x0), shape)
    img = np.cos(ANGLES*5)**2*RADII**2

    mask = np.ones_like((ANGLES))
    mask[100:200] = 0
    mask[:,100:200] = 0
    mask[:,500:643] = 0
    mask[70:130] = 0

    img*=mask
    image_size = (img.nbytes/1024)/1024

    #print image_size  , 'MB'

    start = time.time()

    # reconstruct the image into polar grid
    ttr = time.time()
    rphibinstat = RPhiBinnedStatistic(shape, bins=(400,360), mask=mask, origin=(y0,x0))
    rphi_img = rphibinstat(img)
    # create mask from np.nans since RPhiBinnedStatistic fills masked regions with np.nans
    rphimask = np.ones_like(rphi_img)
    rphimask[np.where(np.isnan(rphi_img))] = 0
    ttrpolar = time.time() - ttr

    ## Regenerate the image to thes the construct_rphi_image

    # get angles and radii from (q, phi) polar coordinate system
    angles = rphibinstat.bin_centers[1]
    radii = rphibinstat.bin_centers[0]

    # reproject
    Zproj = construct_rphi_avg_image(radii, angles, rphi_img, shape=(pixels,pixels))


    # 10  fold symmetry
    # Let's add the same image but before reconstructing, shift phi by 2pi/10....

    sym = int(10)
    polar_shape = 500, 360 
    origin = x0, y0


    reconstructed_image = reconstruct_nfold(img, sym, polar_shape, mask=mask, origin=origin)

    ttc = time.time() - start
    #"Image_Dimensions,Image_size(MB),Iteration,TTC
    system = 'wrangler'
    output_file.write('%d,%d,%f,%s\n'%(pixels,image_size,ttc,system))

    #print 'Total time is: ', ttc , ' seconds'   


