from django.shortcuts import redirect
from xgboost import XGBRegressor
import pandas as pd
import numpy as np
from joblib import dump
from .models import training_testing, predict

# split data 
def split_data(data):
    df = pd.DataFrame(data)
    df_train = pd.DataFrame()
    df_test = pd.DataFrame()

    for prov in df['provinsi'].unique():
        provinsi_data = df[df['provinsi'] == prov]
        n_provinsi = len(provinsi_data)
        n_train = int(0.8 * n_provinsi)
        n_test = n_provinsi - n_train

        # mengambil & memasukkan data sampai ke baris untuk training & testing
        index_train = provinsi_data.index[:n_train]
        index_test = provinsi_data.index[n_train:]

        # menggabungkan data training dan testing 
        df_train = pd.concat([df_train, df.iloc[index_train]])
        df_test = pd.concat([df_test, df.iloc[index_test]])
    
    # reset index 
    df_train = df_train.reset_index(drop=True)
    df_test = df_test.reset_index(drop=True)
    return df_train, df_test

# variabel input
def var_input():
    input_var = ['kode_provinsi','luas_panen', 'produktivitas','curah_hujan','hari_hujan']
    return input_var

# membuat pemodelan dengan xgboost
def model_xgboost(data):
    df_train, df_test = split_data(data)
    df_hasil_pred = pd.DataFrame(columns=['kode_provinsi','bulan_tahun','prediksi_produksi'])

    # membuat objyek algortitma
    xgb = XGBRegressor(n_estimators=70, max_depth=7, reg_lambda=1, learning_rate=0.2, gamma=3)

    # membuat pemodelan dengan xgboost
    for kode in df_train['kode_provinsi'].unique():
        provinsi_train = df_train[df_train['kode_provinsi'] == kode]
        provinsi_test = df_test[df_test['kode_provinsi'] == kode ]

        # memilih input dan target variabel 
        x_train = provinsi_train[var_input()]
        y_train = provinsi_train['produksi']
        x_test = provinsi_test[var_input()]
        y_test = provinsi_test['produksi']

        # membuat model dengan xgboost
        model_xgb = xgb.fit(x_train,y_train)

        # membuat prediksi dengan data set 
        pred_xgb = model_xgb.predict(x_test)

        # menyimpan hasil prediksi sementara 
        df_provinsi_pred = pd.DataFrame({'kode_provinsi':provinsi_test['kode_provinsi'],'bulan_tahun':provinsi_test['bulan_tahun'],'prediksi_produksi':pred_xgb})

        # menggabungkan dataframme prediksi provinsi dengan dataframe asli 
        df_hasil_pred = pd.concat([df_hasil_pred,df_provinsi_pred])

    # menggabungkan dengan data frame test 
    df_test_pred = pd.merge(df_test,df_hasil_pred, on=['kode_provinsi','bulan_tahun'], how='left')
    # simpan model
    dump(model_xgb, 'prediksi_padi/model_ml/xgb_joblib.joblib')
    return df_test_pred

# menghitung nilai MAPE 
def mean_absolute_percentage_error(y_true,y_pred):
  y_true, y_pred = np.array(y_true), np.array(y_pred)
  hitung_jumlah = np.sum(np.abs((y_true - y_pred)/y_true))
  hitung_mape = (hitung_jumlah/len(y_true)) * 100
  return hitung_mape

# menghitung akurasi 
def accuracy(mape):
    akurasi = 100 - mape
    return akurasi