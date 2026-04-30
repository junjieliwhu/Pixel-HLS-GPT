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
pretrained model path: can be found and download here[]
