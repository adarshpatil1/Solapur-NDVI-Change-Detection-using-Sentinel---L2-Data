# Solapur NDVI Change Detection using Sentinel - 2 Data

What this Project is all about?

-It processes the Sentinel 2 raster data data for 31 Dec 2025 and 16 March 2026 of same tile(T43QEV) of Solapur District using Rasterio python library. 
-Computes NDVI, surface reflectance of both timelines.
-Computes the Spectral Signatures.
-Plots the essential graphs (NDVI, Band histogram, NDVI Histogram, Spectral Signatures) for both dates using Matplotlib
-Calculates the NDVI Change from Dec to March.
-Plot the graph of NDVI Change using Matplotlib.
 

## What this Data Includes?

- Sentinel 2 L2A Data (Tile T43QEV extracted B04 and B08 Bands - RED and NIR Bands) 


## Files in this Repo -

Code:

- dec_2025.py                     Computes the NDVI for 31 dec 2025 & Plots the essential graphs.
- march_2026.py                   Computes the NDVI for 16 March 2026 & Plots the essential graphs.
- change_detection.py             Computes NDVI Change and Plots it.

Outputs: 

- histogram_16march2026.png            - Compares the surface reflectance for both bands ( B04 and B08 )  for March Data
- histogram_31dec2025.png              - Compares the surface reflectance for both bands ( B04 and B08 )  for December Data
- ndvi_16march2026.png                 - NDVI Graph over tile for March 
- ndvi_dec2025.png                     - NDVI Graph over tile for December
- ndvi_change_detection.png            - NDVI Change detection graph showing blue is reduced NDVI and when you go towards RED which means increased NDVI
- ndvi_histogram_16march2026.png        - NDVI Value x Pixel Histogram for March
- ndvi_histogram_31dec2025.png          - NDVI Value x Pixel Histogram for December
- spectral_signatures_16march2026.png   - Land Types- Water, Soil, Urban, Vegetation for B04 and B08 vs their Surface Reflectance for March 
- spectral_signatures_31dec2025.png      - Land Types- Water, Soil, Urban, Vegetation for B04 and B08 vs their Surface Reflectance for December

## How to Run 

1. Download Sentinel-2 L2A data for tile T43QEV from https://dataspace.copernicus.eu/
2. Update the file paths in each script to point to your local .SAFE folder location
3. Install dependencies: pip install rasterio numpy matplotlib
4. Run scripts in this order:
   - dec_2025.py
   - march_2026.py
   - change_detection.py


## Results/ Conclusion

Verified the NDVI Decrease from December to March ( The Typical Rabi Crop Cycle).
You can check outputs.
Observed the tile on QGIS to cross-verify the findings.

