'''create input files for HLS-GPT'''
# sm retrieval using landsat, sentinel-2, sentinel-1, and meteorology data, max periods = 366

import numpy as np
import pandas as pd
import os
from tqdm import tqdm
from config import FILL_VALUE, lst, MAX_PERIODS
import re


l30_rename_dict={
    'HLSL30_020_B01':'coastal',
    'HLSL30_020_B02':'blue',
    'HLSL30_020_B03':'green',
    'HLSL30_020_B04':'red',
    'HLSL30_020_B05':'nir',
    'HLSL30_020_B06':'swir1',
    'HLSL30_020_B07':'swir2',
    'HLSL30_020_B10':'bt1',
    'HLSL30_020_B11':'bt2',
    'HLSL30_020_Fmask':'qa',
    'doy':'doy'
}

s30_rename_dict={
    'HLSS30_020_B01':'coastal',
    'HLSS30_020_B02':'blue',
    'HLSS30_020_B03':'green',
    'HLSS30_020_B04':'red',
    'HLSS30_020_B05':'edge1',
    'HLSS30_020_B06':'edge2',
    'HLSS30_020_B07':'edge3',
    'HLSS30_020_B08':'nir8',
    'HLSS30_020_B8A':'nirA',
    'HLSS30_020_B11':'swir1',
    'HLSS30_020_B12':'swir2',
    'HLSS30_020_Fmask':'qa',
    'doy':'doy'
}

def read_L30(df, station_id, year):
    station_id_formatted = clean_name(station_id)
    df['site_clean'] = df['ID'].apply(clean_name)
    landsat_subset = df[(df['year'] == year) & (df['site_clean'] == station_id_formatted)]
    # cloud mask
    mask = create_quality_mask(landsat_subset['HLSL30_020_Fmask'].values)
    df_valid = landsat_subset[mask].copy()
    # unique values
    df_unique = df_valid.drop_duplicates(subset=['doy'], keep='first')
    df_unique = df_unique.rename(columns=l30_rename_dict)
    return df_unique

def read_S30(df, station_id, year):
    station_id_formatted = clean_name(station_id)
    df['site_clean'] = df['ID'].apply(clean_name)
    s2_subset = df[(df['year'] == year) & (df['site_clean'] == station_id_formatted)]
    # cloud mask
    mask = create_quality_mask(s2_subset['HLSS30_020_Fmask'].values)
    df_valid = s2_subset[mask].copy()
    # unique values
    df_unique = df_valid.drop_duplicates(subset=['doy'], keep='first')
    df_unique = df_unique.rename(columns=s30_rename_dict)
    return df_unique


def create_quality_mask(quality_data, bit_nums=None):
    if bit_nums is None:
        bit_nums = [1, 2, 3, 4]   # By default, 1:Cloud, 2:Cloud/Shadow Adjacent, 3:Cloud Shadow, 4:Snow/Ice

    quality_data = np.array(quality_data)
    nan_mask = np.isnan(quality_data)

    # 将 NaN 转为 0（只是为了按位运算）
    q = np.nan_to_num(quality_data, nan=0).astype(np.int32)

    # 构造 bad bits 掩膜
    bits_mask = 0
    for bit in bit_nums:
        bits_mask |= (1 << bit)

    # bad = NaN 或 质量 bit 中包含 bad bit
    bad_mask = nan_mask | ((q & bits_mask) != 0)

    good_mask = ~bad_mask
    return good_mask

def expand_rows_by_doy(arr, common_doys, max_count, bands, doy_col=-1):
    out = np.full((max_count, bands), FILL_VALUE, dtype=np.float32)
    num = min(len(common_doys), max_count)
    out[:num, bands - 1] = np.array(common_doys[:num])
    a_doy = out[:, doy_col]
    b_doy = arr[:, doy_col]
    _, idx_a, idx_b = np.intersect1d(a_doy, b_doy, return_indices=True)
    out[idx_a, :] = arr[idx_b, :]
    return out

def clean_name(s):
    if pd.isna(s):
        return s
    s = str(s)
    # only keep num and letter
    return re.sub(r'[^A-Za-z0-9]', '', s).lower()


def expand_to_full_year_doy(arr, max_days=366, fill_value=-9999):
    """
    arr: (N, 11), last column is DOY (1..366)
    return: (366, 11)
    """
    n_cols = arr.shape[1]

    # 1. 初始化输出数组
    out = np.full((max_days, n_cols), fill_value, dtype=arr.dtype)

    # 2. 填充 DOY 列：1..366
    out[:, -1] = np.arange(1, max_days+1)

    # 3. 原始 DOY（转成 0-based index）
    doys = arr[:, -1].astype(int)
    idx = doys - 1  # DOY=1 → index 0

    # 4. 将已有 DOY 的行拷贝过去
    out[idx, :] = arr

    return out



if __name__ == '__main__':
    points_csv = r'C:\LJJ\foundation model\plots\T10TEM_samples.csv'
    landsat_data_csv = r'C:\LJJ\foundation model\plots\T10TEM_samples_HLSL30.csv'
    s2_data_csv = r'C:\LJJ\foundation model\plots\T10TEM_samples_HLSS30.csv'
    output_dir = r'C:\LJJ\foundation model\plots'

    # landsat
    landsat_data_df = pd.read_csv(landsat_data_csv)
    landsat_data_df['Date'] = pd.to_datetime(landsat_data_df['Date'])
    landsat_data_df['year'] = landsat_data_df['Date'].dt.year
    landsat_data_df['doy'] = landsat_data_df['Date'].dt.dayofyear

    # sentinel-2
    s2_data_df = pd.read_csv(s2_data_csv)
    s2_data_df['Date'] = pd.to_datetime(s2_data_df['Date'])
    s2_data_df['year'] = s2_data_df['Date'].dt.year
    s2_data_df['doy'] = s2_data_df['Date'].dt.dayofyear

    ##############################################################
    # process data by points
    stations_df = pd.read_csv(points_csv)
    stations = stations_df['name'].values.tolist()
    df_list = []
    for station_id in tqdm(stations):
        headers = ['station', 'year'] + lst
        for year in range(2023, 2024):
            # landsat
            l30 = read_L30(landsat_data_df, station_id, year)
            # sentinel-2
            s30 = read_S30(s2_data_df, station_id, year)

            # expand data to MAX length
            # l30
            l30_data = l30[l30_rename_dict.values()].values  # N * 11
            l30_full_year = expand_to_full_year_doy(l30_data, max_days=MAX_PERIODS, fill_value=-9999)
            l30_full_year = l30_full_year.reshape(-1) # reshape

            # s30
            s30_data = s30[s30_rename_dict.values()].values  # N * 13
            s30_full_year = expand_to_full_year_doy(s30_data, max_days=MAX_PERIODS, fill_value=-9999)
            s30_full_year = s30_full_year.reshape(-1)  #
            one_year_total = np.concatenate((l30_full_year, s30_full_year)).reshape(1, -1)

            df_one_year = pd.DataFrame(columns=headers, index=[0])
            df_one_year['station'] = station_id
            df_one_year['year'] = year
            df_one_year[lst] = pd.DataFrame(one_year_total, columns=lst, index=[0])
            df_list.append(df_one_year)

    result_df = pd.concat(df_list)
    result_df.to_csv(os.path.join(output_dir, os.path.basename(points_csv).replace('.csv', '_input_time_series.csv')), index=False)






























