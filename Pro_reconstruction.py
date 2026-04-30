
import numpy as np
import os
import transformer_encoder44
import matplotlib
import matplotlib.pyplot as plt
from config import MAX_PERIODS,L8_fields,S2_fields, MASK_VALUE, START_I_REF
import pandas as pd

L8_bands_n = len(L8_fields)//MAX_PERIODS # 8
S2_bands_n = len(S2_fields)//MAX_PERIODS # 12
matplotlib.rcParams['font.family'] = 'Times New Roman'
plt.rcParams.update({'font.size': 12})
np.set_printoptions(suppress=True)

def apply_transformation(data, slice_range, indices, x_std, x_mean, offset=1):
    if data.ndim == 2:
        for index in indices:
            valid_indices = data[slice_range, index] != -9999.0
            data[slice_range, index][valid_indices] *= x_std[index + offset]
            data[slice_range, index][valid_indices] += x_mean[index + offset]
    if data.ndim == 3: # batch data
        for index in indices:
            valid_indices = data[:, slice_range, index] != -9999.0
            data[:, slice_range, index][valid_indices] *= x_std[index + offset]
            data[:, slice_range, index][valid_indices] += x_mean[index + offset]

def plot_fig(doys, band_idx, predict, obs, only_sentinel=False, band_name=None, save_dir='img', fig_name="plot_band.png", count_place='upper'):
    l8_pred = predict[:MAX_PERIODS, band_idx]
    l8_obs = obs[:MAX_PERIODS, band_idx]
    s2_pred = predict[MAX_PERIODS:, band_idx]
    s2_obs = obs[MAX_PERIODS:, band_idx]
    plt.figure(figsize=(12, 3), dpi=300)
    N_L=0; N_S=0
    if not only_sentinel:
        obs_landsat = l8_obs.reshape(-1)
        valid_landsat = obs_landsat != -9999.0
        N_L = valid_landsat.sum()
        plt.scatter(doys[valid_landsat], obs_landsat[valid_landsat], c="#003366", marker='o', s=10,
                    label=f'Landsat observation')
        plt.scatter(doys[~valid_landsat], l8_pred[~valid_landsat], edgecolors="#ff7f0e", facecolors='none', marker='o', s=8,
                    label=f'Landsat fit')
    obs_sentinel = s2_obs.reshape(-1)
    valid_sentinel = obs_sentinel != -9999.0
    N_S = valid_sentinel.sum()
    plt.scatter(doys[valid_sentinel], obs_sentinel[valid_sentinel], c="#003366", marker='v', s=10,
                label=f'Sentinel observation')
    plt.scatter(doys[~valid_sentinel], s2_pred[~valid_sentinel], edgecolors="#ff7f0e", facecolors='none', marker='v', s=8,
                label=f'Sentinel fit')
    y_coord = 0.95 if count_place == 'upper' else 0.30
    plt.text(
        0.01, y_coord,
        f"N_Landsat={N_L}\nN_Sentinel-2={N_S}",
        transform=plt.gca().transAxes,
        # fontsize=8,
        ha='left',
        va='top',
        color='black',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3', linewidth=0.5, alpha=0.7)
    )

    plt.xlabel("Day of Year")
    if band_name is not None:
        y_label = f'{band_name}'
    else:
        y_label = f"Reflectance (Band {band_idx})"
    plt.ylabel(y_label)
    # plt.ylim(bottom=y_min, top=y_max)
    # plt.title(f"Reconstructing time series observations ")
    plt.legend()
    # plt.grid(True)
    plt.tight_layout()
    plt.show()
    # plt.savefig(f'{save_dir}/{fig_name}', dpi=500)
    # plt.close()

def plot_ndvi(doys, predict, obs, save_idr='img', fig_name="plot_ndvi.png"):
    ndvi_pred = (predict[:, 4] - predict[:, 3]) / (predict[:, 4] + predict[:, 3] + 0.0000001)
    ndvi_pred =ndvi_pred.clip(-1, 1)
    ndvi_obs = (obs[:, 4] - obs[:, 3]) / (obs[:, 4] + obs[:, 3] + 0.0000001)
    ndvi_obs = ndvi_obs.clip(-1, 1)

    plt.figure(figsize=(12, 3), dpi=300)
    valid_landsat = obs[:MAX_PERIODS, 3] != -9999.0
    valid_sentinel = obs[MAX_PERIODS:, 3] != -9999.0
    N_L = valid_landsat.sum()
    N_S = valid_sentinel.sum()
    print(f"N_Landsat={N_L}\nN_Sentinel-2={N_S}")
    plt.scatter(doys[valid_landsat], ndvi_obs[:MAX_PERIODS][valid_landsat], c="#003366", marker='o', s=10,
                label=f'Landsat observation')
    plt.scatter(doys[~valid_landsat], ndvi_pred[:MAX_PERIODS][~valid_landsat], edgecolors="#ff7f0e", facecolors='none', marker='o', s=8,
                label=f'Landsat fit')
    plt.scatter(doys[valid_sentinel], ndvi_obs[MAX_PERIODS:][valid_sentinel], c="#003366", marker='v', s=10,
                label=f'Sentinel observation')
    plt.scatter(doys[~valid_sentinel], ndvi_pred[MAX_PERIODS:][~valid_sentinel], edgecolors="#ff7f0e", facecolors='none', marker='v', s=8,
                label=f'Sentinel fit')
    plt.xlabel("Day of Year")
    plt.ylabel("NDVI")
    # plt.ylim(bottom=0.4, top=1.0)
    plt.text(
        0.01, 0.95,
        f"N_L={N_L}\nN_S={N_S}",
        transform=plt.gca().transAxes,
        # fontsize=8,
        ha='left',
        va='top',
        color='black',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3', linewidth=0.5, alpha=0.7)
    )
    plt.legend()
    # plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.1), ncol=2)
    plt.tight_layout()
    # plt.savefig(f'{save_idr}/{fig_name}', dpi=500)
    plt.show()
    # plt.close()


def read_data_from_csv(csv_file):
    df = pd.read_csv(csv_file)
    names = df['station'].values
    trainx_l8 = np.array(df[L8_fields]).astype(np.float32)
    input_l8_train = trainx_l8.reshape(trainx_l8.shape[0], MAX_PERIODS, L8_bands_n)
    trainx_s2 = np.array(df[S2_fields]).astype(np.float32)
    input_s2_train = trainx_s2.reshape(trainx_s2.shape[0], MAX_PERIODS, S2_bands_n)
    l8_valid_index = input_l8_train[:, :, START_I_REF] != MASK_VALUE
    s2_valid_index = input_s2_train[:, :, START_I_REF] != MASK_VALUE
    train_n = input_l8_train.shape[0]
    train_norm0 = np.full([train_n, MAX_PERIODS + MAX_PERIODS, S2_bands_n], fill_value=MASK_VALUE, dtype=np.float32)
    mean_std_df = pd.read_csv(mean_std_file, skiprows=1, header=None, names=['mean', 'std'])
    x_mean = mean_std_df['mean'].values
    x_std = mean_std_df['std'].values
    l8_mean = x_mean[:8]
    l8_std = x_std[:8]
    s2_mean = x_mean[8:]
    s2_std = x_std[8:]

    for bi in range(S2_bands_n):
        if bi < START_I_REF:
            train_norm0[:, :, bi] = np.concatenate((input_l8_train[:, :, bi], input_s2_train[:, :, bi]), axis=1)
        elif bi < L8_bands_n:
            train_norm0[:, :MAX_PERIODS, bi][l8_valid_index] = (input_l8_train[:, :, bi][l8_valid_index] - l8_mean[
                bi]) / l8_std[bi]

            train_norm0[:, MAX_PERIODS:, bi][s2_valid_index] = (input_s2_train[:, :, bi][s2_valid_index] - s2_mean[
                bi]) / s2_std[bi]
        else:
            train_norm0[:, :MAX_PERIODS, bi] = MASK_VALUE
            train_norm0[:, MAX_PERIODS:, bi][s2_valid_index] = (input_s2_train[:, :, bi][s2_valid_index] - s2_mean[
                bi]) / s2_std[bi]
    doys = train_norm0[:, :MAX_PERIODS, 0].copy().squeeze()
    doy_norm = (train_norm0[:, :, 0] - 1) / 366.
    train_norm0[:, :, 0] = doy_norm
    obs_data = train_norm0[:, :, 1:].copy().squeeze()  # remove doy
    l8_slice = slice(0, MAX_PERIODS)
    s2_slice = slice(MAX_PERIODS, MAX_PERIODS + MAX_PERIODS)
    apply_transformation(obs_data, l8_slice, range(L8_bands_n - 1), x_std, x_mean, offset=1)
    apply_transformation(obs_data, s2_slice, range(S2_bands_n - 1), x_std, x_mean, offset=9)
    return train_norm0, obs_data, doys, names


def load_model(model_path, periods):
    model_basic = transformer_encoder44.get_transformer_reflectance(MAX_LANDSAT=176, MAX_SENTINEL2=176, L8_bands_n=8,
                                                                  S2_bands_n=12,
                                                                  layern1=3, layern2=4, units=256,
                                                                  n_head=8, drop=0.1, is_day_input=1,
                                                                  is_sensor=True, is_xy=False, active="sigmoid",
                                                                  concat=4)
    model_basic.load_weights(model_path)
    if periods == 176:
        return model_basic
    model_long = transformer_encoder44.get_transformer_reflectance(MAX_LANDSAT=periods, MAX_SENTINEL2=periods, L8_bands_n=8,
                                                                  S2_bands_n=12,
                                                                  layern1=3, layern2=4, units=256,
                                                                  n_head=8, drop=0.1, is_day_input=1,
                                                                  is_sensor=True, is_xy=False, active="sigmoid",
                                                                  concat=4)
    for il, ilayer in enumerate(model_basic.layers):
        ilayer1 = model_basic.layers[il]
        ilayer2 = model_long.layers[il]
        name_cls = ''.join([ic for ic in ilayer1.name if not ic.isdigit() and ic != '_'])
        name_ref = ''.join([ic for ic in ilayer2.name if not ic.isdigit() and ic != '_'])
        if "embedding" in name_cls:
            embedding_name = ilayer1.name
        if name_cls == name_ref and ilayer1.trainable and ilayer2.trainable and not not ilayer1.weights and not not ilayer2.weights:
            # print ("\t"+ilayer.name, end=" ")
            model_long.layers[il].set_weights(model_basic.layers[il].get_weights())
    print('using long model...')
    return model_long



if __name__ == '__main__':

    csv_path = r'C:\LJJ\foundation model\plots\T10TEM_samples_input_time_series.csv'
    mean_std_file = 'mean_std_v1_6_filtered.csv'
    model_path = r'C:\LJJ\hls_reconstruct\model\best_model_GAPS_P0.5_versionv7_27.h5'
    output_dir = r'C:\LJJ\foundation model\plots'


    train_norm0, obs_data, doys, names = read_data_from_csv(csv_path)
    model = load_model(model_path, MAX_PERIODS)
    pred_y = model.predict(train_norm0, verbose=0) # N*730*11

    l8_obs = obs_data[:, :MAX_PERIODS, :L8_bands_n - 1].copy()
    l8_pred = pred_y[:, :MAX_PERIODS, :L8_bands_n - 1]
    l8_mask = l8_obs[:, :, 0] == MASK_VALUE  # true is missing obs, filled with pred, false will keep obs data
    l8_reconstructed = np.where(
        l8_mask[:, :, None],
        l8_pred,
        l8_obs
    )
    l8_reconstructed = np.concatenate((l8_reconstructed, l8_mask[:, :, None]), axis=2)
    print('l8 reconstructed shape:', l8_reconstructed.shape)
    s2_obs = obs_data[:, MAX_PERIODS:, :].copy()
    s2_pred = pred_y[:, MAX_PERIODS:, :]
    s2_mask = s2_obs[:, :, 0] == MASK_VALUE
    s2_reconstructed = np.where(
        s2_mask[:, :, None],
        s2_pred,
        s2_obs
    )
    s2_reconstructed = np.concatenate((s2_reconstructed, s2_mask[:, :, None]), axis=2)
    print('s2 reconstructed shape:', s2_reconstructed.shape)

    np.save(os.path.join(output_dir, 'T10TEM_samples_HLS-GPT_Reconstructed_Landsat.npy'), l8_reconstructed)
    np.save(os.path.join(output_dir, 'T10TEM_samples_HLS-GPT_Reconstructed_Sentinel-2.npy'), s2_reconstructed)
    np.save(os.path.join(output_dir, 'T10TEM_samples_HLS-GPT_Names.npy'), names)

    # plot examples
    print(f'plot example for {names[0]}')
    plot_fig(doys[0], 3, pred_y[0], obs_data[0], band_name='Red reflectance')
    plot_fig(doys[0], 4, pred_y[0], obs_data[0], band_name='NIR reflectance')
    plot_ndvi(doys[0], pred_y[0], obs_data[0])

    print(f'plot example for {names[1]}')
    plot_fig(doys[1], 3, pred_y[1], obs_data[1], band_name='Red reflectance')
    plot_fig(doys[1], 4, pred_y[1], obs_data[1], band_name='NIR reflectance')
    plot_ndvi(doys[1], pred_y[1], obs_data[1])



