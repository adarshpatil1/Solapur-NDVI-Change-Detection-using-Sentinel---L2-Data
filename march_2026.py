import rasterio 
import numpy as np
import matplotlib.pyplot as plt


dataset1_march = rasterio.open(r"C:\Users\ashis\Downloads\S2B_MSIL2A_20260316T051649_N0512_R062_T43QEV_20260316T091005.SAFE/GRANULE/L2A_T43QEV_A047135_20260316T052630/IMG_DATA/R10m/T43QEV_20260316T051649_B04_10m.jp2")
b04_march = dataset1_march.read(1).astype(float)    

trueb04_march = (b04_march - 1000)/10000   #BOA OFFEST - 1000 , QUANTIFICATION = 10000

dataset2_march = rasterio.open(r"C:\Users\ashis\Downloads\S2B_MSIL2A_20260316T051649_N0512_R062_T43QEV_20260316T091005.SAFE/GRANULE/L2A_T43QEV_A047135_20260316T052630/IMG_DATA/R10m/T43QEV_20260316T051649_B08_10m.jp2")
b08_march = dataset2_march.read(1).astype(float)

trueb08_march = (b08_march - 1000)/10000   #BOA OFFEST - 1000 , QUANTIFICATION = 10000

print(b04_march.shape, b04_march.min(), b04_march.max(), b04_march.mean())        
print(b08_march.shape, b08_march.min(), b08_march.max(), b08_march.mean())

print(trueb04_march.shape, trueb04_march.min(), trueb04_march.max(), trueb04_march.mean())        
print(trueb08_march.shape, trueb08_march.min(), trueb08_march.max(), trueb08_march.mean())      

print((trueb04_march > 1.0).sum())   #Counting the anamoly pixels we were getting
print((trueb08_march > 1.0).sum())   #Counting the anamoly pixels we were getting

print((trueb04_march <= -0.1).sum())  #Counting the anamoly pixels we were getting
print((trueb08_march <= -0.1).sum())  #Counting the anamoly pixels we were getting

trueb04_march[trueb04_march > 1.0] = np.nan
trueb08_march[trueb08_march > 1.0] = np.nan
trueb04_march[trueb04_march <= -0.1] = np.nan
trueb08_march[trueb08_march <= -0.1] = np.nan

print(trueb04_march.shape, np.nanmin(trueb04_march), np.nanmax(trueb04_march), np.nanmean(trueb04_march))        
print(trueb08_march.shape, np.nanmin(trueb08_march), np.nanmax(trueb08_march), np.nanmean(trueb08_march))

ndvi_march = (trueb08_march - trueb04_march)/(trueb08_march + trueb04_march)


ndvi_march[ndvi_march == -np.inf] = np.nan
ndvi_march[ndvi_march == np.inf]  = np.nan
ndvi_march[ndvi_march < -1 ] = np.nan
ndvi_march[ndvi_march > 1 ]  = np.nan

print(np.nanmin(ndvi_march), np.nanmax(ndvi_march), np.nanmean(ndvi_march))

plt.imshow(ndvi_march,  cmap="RdYlGn")
plt.title("NDVI - Solapur - 16 March 2026")
plt.colorbar()
plt.savefig("ndvi_16march2026.png")
plt.clf()


clean_b04 = trueb04_march[~np.isnan(trueb04_march)].flatten()  #flattens 2d to 1d
clean_b08 = trueb08_march[~np.isnan(trueb08_march)].flatten()
plt.hist(clean_b04, color = "Red", alpha = 0.6)
plt.hist(clean_b08, color = "Maroon", alpha = 0.6)
plt.title("Bands Histogram - Solapur - 16 March 2026")
plt.xlabel("Surface Reflectance")
plt.ylabel("Pixel Count")
plt.legend(["B04 - Red", "B08 - Maroon"])
plt.savefig("histogram_16march2026.png")
plt.clf()

clean_ndvi = ndvi_march[~np.isnan(ndvi_march)].flatten()
plt.hist(clean_ndvi, color="Green")
plt.title("NDVI Distribution - Solapur - 16 Mar 2026")
plt.xlabel("NDVI Value")
plt.ylabel("Pixel Count")
plt.savefig("ndvi_histogram_16march2026.png")
plt.clf()


row_water, col_water = dataset1_march.index(596315, 1959919)  #Water Body
row_urban, col_urban = dataset1_march.index(597336, 1952676)  #Urban Area
row_soil, col_soil = dataset1_march.index(591941, 1969797)  #Dry Soil
row_veg, col_veg = dataset1_march.index(552839, 1938202)  #Dense Vegetation

print(row_water, col_water)
print(row_urban, col_urban)
print(row_soil, col_soil)
print(row_veg, col_veg)

print(trueb04_march[row_water, col_water], trueb08_march[row_water, col_water])
print(trueb04_march[row_urban, col_urban], trueb08_march[row_urban, col_urban])
print(trueb04_march[row_soil, col_soil], trueb08_march[row_soil, col_soil])
print(trueb04_march[row_veg, col_veg], trueb08_march[row_veg, col_veg])


w = w_b04, w_b08 = trueb04_march[row_water, col_water], trueb08_march[row_water, col_water]
u = u_b04, u_b08 = trueb04_march[row_urban, col_urban], trueb08_march[row_urban, col_urban]
s = s_b04, s_b08 = trueb04_march[row_soil, col_soil], trueb08_march[row_soil, col_soil]
v = v_b04, v_b08 = trueb04_march[row_veg, col_veg], trueb08_march[row_veg, col_veg]

w_ndvi = (w_b08 - w_b04)/(w_b08 + w_b04)
u_ndvi = (u_b08 - u_b04)/(u_b08 + u_b04)
s_ndvi = (s_b08 - s_b04)/(s_b08 + s_b04)
v_ndvi = (v_b08 - v_b04)/(v_b08 + v_b04)

print(w_ndvi)
print(u_ndvi)
print(s_ndvi)
print(v_ndvi)

b04_values = [w_b04, u_b04, s_b04, v_b04]
b08_values = [w_b08, u_b08, s_b08, v_b08]
labels = ['Water', 'Urban', 'Soil', 'Vegetation']
fig, ax = plt.subplots(layout = "constrained")
x = np.arange(len(labels))
width = 0.25
ax.bar(x - width/2, b04_values, width, label = 'b04 Red')
ax.bar(x + width/2, b08_values, width, label = 'b08 NIR')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()
ax.set_title('Spectral Signatures - Solapur - 16 March 2026')
ax.set_ylabel('Surface Reflectance')
plt.savefig('spectral_signatures_16march2026.png')
plt.clf()