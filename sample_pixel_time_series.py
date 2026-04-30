'''
download pixel time series from AppEEARS or sample local HLS pixel time series values using this code
'''
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime, timedelta
import re, os
from pathlib import Path
import rasterio
from rasterio.warp import transform
from tqdm import tqdm

L30_bands = ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B09', 'B10', 'B11', 'Fmask', 'SAA', 'SZA', 'VAA', 'VZA']
S30_bands = ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B09', 'B10', 'B11', 'B12', 'B8A', 'Fmask', 'SAA', 'SZA', 'VAA', 'VZA']

def get_files_1year(tile, startdoy, enddoy, file_list, hls='l30'):
    # Build a regex to extract the date from filenames matching the given tile.
    # e.g., for tile T15TUE, a file name may contain "HLS.S30.T15TUE.2023244T170859..."
    if hls == 'l30':
        pattern = re.compile(r"HLS\.L30\." + re.escape(tile) + r"\.(\d{7})T\d{6}")
    else:
        pattern = re.compile(r"HLS\.S30\." + re.escape(tile) + r"\.(\d{7})T\d{6}")
    selected_files = []
    seen_basenames = set()
    for fname in file_list:
        if tile in fname:
            m = pattern.search(fname)
            if m:
                # print
                file_date_str = m.group(1)  # e.g., "2023244"
                if int(startdoy) <= int(file_date_str) < int(enddoy):
                    base_name = os.path.basename(fname)
                    if base_name not in seen_basenames:
                        seen_basenames.add(base_name)
                        selected_files.append(fname)

    selected_files.sort()
    return selected_files, len(selected_files)

def get_tile_id_from_latlon(shp_path, lat, lon, tile_field="tile_id"):
    gdf = gpd.read_file(shp_path)
    if tile_field not in gdf.columns:
        raise ValueError(f"Field '{tile_field}' not found in shapefile columns: {list(gdf.columns)}")
    if gdf.crs is None:
        raise ValueError("Shapefile CRS is None. Please define CRS for the shapefile first.")
    # 点是 WGS84
    point_gdf = gpd.GeoDataFrame(
        {"geometry": [Point(float(lon), float(lat))]},
        crs="EPSG:4326"
    )
    # 统一到 shp 的 CRS
    point_in_shp_crs = point_gdf.to_crs(gdf.crs)
    pt = point_in_shp_crs.geometry.iloc[0]
    # contains 对边界点返回 False；covers 能覆盖边界/内部
    hits = gdf[gdf.geometry.covers(pt)]
    if len(hits) == 0:
        return None
    return str(hits.iloc[0][tile_field])

def read_singleband_value_by_lonlat(fmask_path, band_name, lon, lat, src_crs: str = "EPSG:4326", sensor='l30'):
    tif_path = fmask_path.replace('Fmask', band_name)
    val = -9999
    with rasterio.open(tif_path) as ds:
        if ds.crs is None:
            raise ValueError("Raster CRS is None. Please ensure the raster has a valid CRS.")
        x, y = transform(src_crs, ds.crs, [lon], [lat])  # 返回 list
        x, y = x[0], y[0]
        row, col = ds.index(x, y)
        val = ds.read(1, window=((row, row + 1), (col, col + 1)))[0, 0]
    if band_name in ['SAA', 'SZA', 'VAA', 'VZA']:
        if val != 40000: # 40000 is filled value for sun and view angles  https://lpdaac.usgs.gov/documents/1698/HLS_User_Guide_V2.pdf
            val = val * 0.01
        return val
    if band_name == 'Fmask':
        return val
    if sensor == 'l30' and band_name in ['B10', 'B11']:  # top of Atmosphere Brightness temperature
        val = val * 0.01
        return val
    val =  val * 0.0001
    return val



if __name__ == '__main__':
    pixel_points_csv = 'temp.csv'
    CONUS_tiles_shp_path = 'CONUS_hls_tiles/CONUS_hls_tiles.shp'
    output_dir = '/home/junjie.li/Pixel_HLS_GPT'
    startdoy = 2023001
    enddoy = 2024001

    # hls_download_dir = '/home/junjie.li/prepare_data/hls_download_txt'
    # hls_txt_list = os.listdir(hls_download_dir)
    # HLS_LIST = []
    # for file in hls_txt_list:
    #     txt_path = os.path.join(hls_download_dir, file)
    #     with open(txt_path, 'r') as f:
    #         files = f.read().splitlines()
    #         HLS_LIST.extend(files)

    hls_data_dir = ''
    search_dir = Path(hls_data_dir)
    HLS_LIST = [str(p) for p in search_dir.rglob('*.Fmask.tif')]

    pixels_df = pd.read_csv(pixel_points_csv)
    l30_list = []
    S30_list = []
    for index, row in tqdm(pixels_df.iterrows()):
        name = row['name']
        lat = row['Lat']
        lon = row['Lon']
        tile_id = get_tile_id_from_latlon(CONUS_tiles_shp_path, lat, lon, tile_field="tile_id")
        if tile_id is None:
            raise FileNotFoundError(f"Could not find tile_id: {name}")
        l30_files, _ = get_files_1year(tile_id, startdoy, enddoy, HLS_LIST, hls='l30')
        for fname in l30_files:
            pattern = re.compile(r"HLS\.[SL]30\." + re.escape(tile_id) + r"\.(\d{7})T\d{6}")
            m = pattern.search(fname)
            file_date_str = m.group(1)
            file_date = datetime.strptime(file_date_str, "%Y%j")
            l30_dict = {}
            l30_dict['ID'] = name
            l30_dict['Latitude'] = lat
            l30_dict['Longitude'] = lon
            l30_dict['Date'] = file_date
            l30_dict['HLS_Tile'] = tile_id
            for band in L30_bands:
                l30_dict[f'HLSL30_020_{band}'] = read_singleband_value_by_lonlat(fname, band, lon, lat, sensor='l30')
            l30_list.append(l30_dict)

        s30_files, _ = get_files_1year(tile_id, startdoy, enddoy, HLS_LIST, hls='S30')
        for fname in s30_files:
            pattern = re.compile(r"HLS\.[SL]30\." + re.escape(tile_id) + r"\.(\d{7})T\d{6}")
            m = pattern.search(fname)
            file_date_str = m.group(1)
            file_date = datetime.strptime(file_date_str, "%Y%j")
            s30_dict = {}
            s30_dict['ID'] = name
            s30_dict['Latitude'] = lat
            s30_dict['Longitude'] = lon
            s30_dict['Date'] = file_date
            s30_dict['HLS_Tile'] = tile_id
            for band in S30_bands:
                s30_dict[f'HLSS30_020_{band}'] = read_singleband_value_by_lonlat(fname, band, lon, lat, sensor='S30')
            S30_list.append(s30_dict)

    l30_df = pd.DataFrame(l30_list)
    l30_df.to_csv(os.path.join(output_dir, os.path.basename(pixel_points_csv).replace('.csv', f'_{startdoy}_{enddoy}_HLSL30.csv')), index=False)

    s30_df = pd.DataFrame(S30_list)
    s30_df.to_csv(os.path.join(output_dir, os.path.basename(pixel_points_csv).replace('.csv', f'_{startdoy}_{enddoy}_HLSS30.csv')), index=False)














