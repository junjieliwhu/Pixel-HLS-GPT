# Pixel-HLS-GPT
Reconstruct HLS single pixel reflectance time series using HLS-GPT

1.Prepare HLS time series data
generate HLSL30.csv and HLSS30.csv
there are two ways:
(1) download pixel time series from NASA AppEEARS[https://appeears.earthdatacloud.nasa.gov/]
OR
(2) sample pixel time series from local disk using sample_pixel_time_series.py
input parameters include:
pixel_points_csv: csv files include point name, Lat, Lon, each single point is a raw, WGS84
CONUS_tiles_shp_path: helps to identify which tile the point located
startdoy
enddoy

2. Prepare input data for HLS-GPT
run create_input_files.py to generate HLS-GPT input time series
input parameters include:
pixel_points_csv (include name, Lat, Lon)
HLSL30.csv and HLSS30.csv

3. HLS-GPT reconstruction
run Pro_reconstruction.py
input parameters include:
HLS time series last step generated
mean_std_file: mean_std_v1_6_filtered.csv
pretrained model path: best_model_GAPS_P0.5_versionv7_27.h5, can be found and download here[https://zenodo.org/records/15678251]

4. result format
There are three .npy output files
(1)HLS-GPT_Reconstructed_Landsat.npy
shape:(N, 365, 8), 8 bands are: coastal, blue, green, red, nir, swir1, swir2, tag
(2)HLS-GPT_Reconstructed_Sentinel-2.npy
shape:(N, 365, 12), 12 bands are: coastal, blue, green, red, nirA, swir1, swir2, edge1, edge2, edge3, nir8, tag
(3)Points_Names.npy
shape:(N,), saved the corresponding point names for reconstructed HLS.
In file 1 and 2, good-quality observations are not reconstructed. Only missing observations are filled using model outputs. The last band (tag) equals 1 if is reconstructed else 0.

some examples
![fig1](/img/T10TDM_2023_row3312_col553_NIR_model3.png)
![fig1](/img/T18TWN_2023_row3100_col1300_NIR_model3.png)
![fig1](/img/T18TWN_2023_row3100_col1300_RED_model3.png)
![fig1](/img/T18TWN_2023_row3100_col1300_NDVI_model3.png)
