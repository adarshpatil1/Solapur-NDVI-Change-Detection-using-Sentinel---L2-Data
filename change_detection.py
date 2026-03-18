import rasterio 
import numpy as np
import matplotlib.pyplot as plt


dataset1_dec = rasterio.open(r"C:\Users\ashis\Downloads\S2C_MSIL2A_20251231T052231_N0511_R062_T43QEV_20251231T083411.SAFE/GRANULE/L2A_T43QEV_A006896_20251231T053319/IMG_DATA/R10m/T43QEV_20251231T052231_B04_10m.jp2")
b04_dec = dataset1_dec.read(1).astype(float)    

trueb04_dec = (b04_dec - 1000)/10000   #BOA OFFEST - 1000 , QUANTIFICATION = 10000

dataset2_dec = rasterio.open(r"C:\Users\ashis\Downloads\S2C_MSIL2A_20251231T052231_N0511_R062_T43QEV_20251231T083411.SAFE/GRANULE/L2A_T43QEV_A006896_20251231T053319/IMG_DATA/R10m/T43QEV_20251231T052231_B08_10m.jp2")
b08_dec = dataset2_dec.read(1).astype(float)

trueb08_dec = (b08_dec - 1000)/10000   #BOA OFFEST - 1000 , QUANTIFICATION = 10000

trueb04_dec[trueb04_dec > 1.0] = np.nan
trueb08_dec[trueb08_dec > 1.0] = np.nan
trueb04_dec[trueb04_dec <= -0.1] = np.nan
trueb08_dec[trueb08_dec <= -0.1] = np.nan

ndvi_dec= (trueb08_dec - trueb04_dec)/(trueb08_dec + trueb04_dec)

ndvi_dec[ndvi_dec == -np.inf] = np.nan
ndvi_dec[ndvi_dec == np.inf]  = np.nan
ndvi_dec[ndvi_dec < -1 ] = np.nan
ndvi_dec[ndvi_dec > 1 ]  = np.nan

dataset1_march = rasterio.open(r"C:\Users\ashis\Downloads\S2B_MSIL2A_20260316T051649_N0512_R062_T43QEV_20260316T091005.SAFE/GRANULE/L2A_T43QEV_A047135_20260316T052630/IMG_DATA/R10m/T43QEV_20260316T051649_B04_10m.jp2")
b04_march = dataset1_march.read(1).astype(float)    

trueb04_march = (b04_march - 1000)/10000   #BOA OFFEST - 1000 , QUANTIFICATION = 10000

dataset2_march = rasterio.open(r"C:\Users\ashis\Downloads\S2B_MSIL2A_20260316T051649_N0512_R062_T43QEV_20260316T091005.SAFE/GRANULE/L2A_T43QEV_A047135_20260316T052630/IMG_DATA/R10m/T43QEV_20260316T051649_B08_10m.jp2")
b08_march = dataset2_march.read(1).astype(float)

trueb08_march = (b08_march - 1000)/10000   #BOA OFFEST - 1000 , QUANTIFICATION = 10000

trueb04_march[trueb04_march > 1.0] = np.nan
trueb08_march[trueb08_march > 1.0] = np.nan
trueb04_march[trueb04_march <= -0.1] = np.nan
trueb08_march[trueb08_march <= -0.1] = np.nan

ndvi_march = (trueb08_march - trueb04_march)/(trueb08_march + trueb04_march)


ndvi_march[ndvi_march == -np.inf] = np.nan
ndvi_march[ndvi_march == np.inf]  = np.nan
ndvi_march[ndvi_march < -1 ] = np.nan
ndvi_march[ndvi_march > 1 ]  = np.nan


ndvi_change = ndvi_march - ndvi_dec


# Spatial Alignment Check 

assert dataset1_dec.shape == dataset1_march.shape
assert dataset1_dec.transform == dataset1_march.transform
print("Spatial alignment confirmed.")

print(np.nanmin(ndvi_change), np.nanmax(ndvi_change), np.nanmean(ndvi_change))
print(np.isnan(ndvi_change).sum())


plt.imshow(ndvi_change, cmap = "coolwarm")
plt.colorbar()
plt.title("NDVI Change Detection - Solapur - 31 Dec 2025 to 16 March 2026")
plt.savefig("ndvi_change_detection.png")
plt.clf()

# Threshold Classification

ndvi_classified = np.zeros_like(ndvi_change)

ndvi_classified[ndvi_change < -0.2] = -1
ndvi_classified[ndvi_change >  0.2] = 1
ndvi_classified[np.isnan(ndvi_change)] = np.nan

plt.imshow(ndvi_classified, cmap = "RdYlGn")
plt.title("NDVI Threshold Classification - Solapur - Dec 2025 & March 2026")
plt.colorbar()
plt.savefig("ndvi_threshold_classified.png")
plt.clf()