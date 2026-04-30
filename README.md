# Pixel-HLS-GPT

Reconstruct single-pixel HLS reflectance time series using the pretrained HLS-GPT model.

---

## Workflow Overview

The workflow consists of three main steps:

1. Prepare HLS time series data  
2. Generate model input files  
3. Run HLS-GPT reconstruction  

---

## 1. Prepare HLS Time Series Data

Generate:

- `HLSL30.csv` (Landsat)  
- `HLSS30.csv` (Sentinel-2)  

There are two ways:

### (1) Download from NASA AppEEARS

https://appeears.earthdatacloud.nasa.gov/

---

### (2) Sample from local HLS data

Run:

```bash
python sample_pixel_time_series.py
```

#### Input parameters:

- `pixel_points_csv`  
  CSV file including: name, lat, lon (WGS84). Each row is one pixel.

- `CONUS_tiles_shp_path`  
  Used to identify which HLS tile the point is located in.

- `startdoy`  
- `enddoy`  

---

## 2. Prepare Input for HLS-GPT

Run:

```bash
python create_input_files.py
```

#### Input:

- `pixel_points_csv`  
- `HLSL30.csv`  
- `HLSS30.csv`  

---

## 3. HLS-GPT Reconstruction

Run:

```bash
python Pro_reconstruction.py
```

#### Input:

- Processed HLS time series (from Step 2)  
- `mean_std_file`  
  Example: `mean_std_v1_6_filtered.csv`  

- Pretrained model  
  Example: `best_model_GAPS_P0.5_versionv7_27.h5`  
  Download: https://zenodo.org/records/15678251  

---

## Output Format

Three `.npy` files will be generated:

### (1) HLS-GPT_Reconstructed_Landsat.npy

- Shape: `(N, 365, 8)`  
- Bands:  
  `coastal, blue, green, red, nir, swir1, swir2, tag`

---

### (2) HLS-GPT_Reconstructed_Sentinel-2.npy

- Shape: `(N, 365, 12)`  
- Bands:  
  `coastal, blue, green, red, nirA, swir1, swir2, edge1, edge2, edge3, nir8, tag`

---

### (3) Points_Names.npy

- Shape: `(N,)`  
- Stores point names corresponding to reconstructed time series  

---

## Notes

- Only **missing observations** are reconstructed  
- Original good-quality observations are preserved  
- The last band (`tag`) indicates:  
  - `1` → reconstructed  
  - `0` → original observation  

---

## Citation

If you use this code, please cite:

Li, J., Zhang, H. K., & Roy, D. P. (2026).  
*HLS-GPT: A Generative Pretrained Transformer (GPT) Model for Accurate Harmonized Landsat and Sentinel-2 (HLS) Reflectance Time Series Reconstruction.*  
(In review)

---

## Examples

![Example 1](/img/T10TDM_2023_row3312_col553_NIR_model3.png)  
![Example 2](/img/T18TWN_2023_row3100_col1300_NIR_model3.png)  
![Example 3](/img/T18TWN_2023_row3100_col1300_RED_model3.png)  
![Example 4](/img/T18TWN_2023_row3100_col1300_NDVI_model3.png)



