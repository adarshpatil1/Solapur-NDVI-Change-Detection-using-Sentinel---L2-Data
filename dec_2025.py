import rasterio 
import numpy as np
import matplotlib.pyplot as plt

dataset1 = rasterio.open(r"C:\Users\ashis\Downloads\S2C_MSIL2A_20251231T052231_N0511_R062_T43QEV_20251231T083411.SAFE/GRANULE/L2A_T43QEV_A006896_20251231T053319/IMG_DATA/R10m/T43QEV_20251231T052231_B04_10m.jp2")
b04 = dataset1.read(1).astype(float)    

trueb04 = (b04 - 1000)/10000   #BOA OFFEST - 1000 , QUANTIFICATION = 10000

dataset2 = rasterio.open(r"C:\Users\ashis\Downloads\S2C_MSIL2A_20251231T052231_N0511_R062_T43QEV_20251231T083411.SAFE/GRANULE/L2A_T43QEV_A006896_20251231T053319/IMG_DATA/R10m/T43QEV_20251231T052231_B08_10m.jp2")
b08 = dataset2.read(1).astype(float)

trueb08 = (b08 - 1000)/10000   #BOA OFFEST - 1000 , QUANTIFICATION = 10000

print(b04.shape, b04.min(), b04.max(), b04.mean())        
print(b08.shape, b08.min(), b08.max(), b08.mean())

print(trueb04.shape, trueb04.min(), trueb04.max(), trueb04.mean())        
print(trueb08.shape, trueb08.min(), trueb08.max(), trueb08.mean())      

print((trueb04 > 1.0).sum())   #Counting the anamoly pixels we were getting
print((trueb08 > 1.0).sum())   #Counting the anamoly pixels we were getting

print((trueb04 <= -0.1).sum())  #Counting the anamoly pixels we were getting
print((trueb08 <= -0.1).sum())  #Counting the anamoly pixels we were getting

trueb04[trueb04 > 1.0] = np.nan
trueb08[trueb08 > 1.0] = np.nan
trueb04[trueb04 <= -0.1] = np.nan
trueb08[trueb08 <= -0.1] = np.nan

print(trueb04.shape, np.nanmin(trueb04), np.nanmax(trueb04), np.nanmean(trueb04))        
print(trueb08.shape, np.nanmin(trueb08), np.nanmax(trueb08), np.nanmean(trueb08))

ndvi = (trueb08 - trueb04)/(trueb08 + trueb04)


ndvi[ndvi == -np.inf] = np.nan
ndvi[ndvi == np.inf]  = np.nan
ndvi[ndvi < -1 ] = np.nan
ndvi[ndvi > 1 ]  = np.nan

print(np.nanmin(ndvi), np.nanmax(ndvi), np.nanmean(ndvi))

plt.imshow(ndvi,  cmap="RdYlGn")
plt.title("NDVI - Solapur - 31st Dec 2025")
plt.colorbar()
plt.savefig("ndvi_dec2025.png")
plt.clf()


clean_b04 = trueb04[~np.isnan(trueb04)].flatten()  #flattens 2d to 1d
clean_b08 = trueb08[~np.isnan(trueb08)].flatten()
plt.hist(clean_b04, color = "Red", alpha = 0.6)
plt.hist(clean_b08, color = "Maroon", alpha = 0.6)
plt.title("Band Histograms - Solapur - 31 Dec 2025")
plt.xlabel("Surface Reflectance")
plt.ylabel("Pixel Count")
plt.legend(["B04 - Red", "B08 - Maroon"])
plt.savefig("histogram_31dec2025.png")
plt.clf()

clean_ndvi = ndvi[~np.isnan(ndvi)].flatten()
plt.hist(clean_ndvi, color="Green")
plt.title("NDVI Distribution - Solapur - 31 Dec 2025")
plt.xlabel("NDVI Value")
plt.ylabel("Pixel Count")
plt.savefig("ndvi_histogram_31dec2025.png")
plt.clf()


row_water, col_water = dataset1.index(596315, 1959919)  #Water Body
row_urban, col_urban = dataset1.index(597336, 1952676)  #Urban Area
row_soil, col_soil = dataset1.index(591941, 1969797)  #Dry Soil
row_veg, col_veg = dataset1.index(552839, 1938202)  #Dense Vegetation

print(row_water, col_water)
print(row_urban, col_urban)
print(row_soil, col_soil)
print(row_veg, col_veg)

print(trueb04[row_water, col_water], trueb08[row_water, col_water])
print(trueb04[row_urban, col_urban], trueb08[row_urban, col_urban])
print(trueb04[row_soil, col_soil], trueb08[row_soil, col_soil])
print(trueb04[row_veg, col_veg], trueb08[row_veg, col_veg])


w = w_b04, w_b08 = trueb04[row_water, col_water], trueb08[row_water, col_water]
u = u_b04, u_b08 = trueb04[row_urban, col_urban], trueb08[row_urban, col_urban]
s = s_b04, s_b08 = trueb04[row_soil, col_soil], trueb08[row_soil, col_soil]
v = v_b04, v_b08 = trueb04[row_veg, col_veg], trueb08[row_veg, col_veg]

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
ax.set_title('Spectral Signatures - Solapur - 31 Dec 2025')
ax.set_ylabel('Surface Reflectance')
plt.savefig('spectral_signatures_31dec2025.png')
plt.clf()