from asyncio.windows_events import NULL
from datetime import datetime
from email import message
import imp
from django.http import HttpResponse
from importlib.metadata import files
from multiprocessing import context
from urllib import response
from django.shortcuts import render, redirect
from .forms import UploadFileForm, PredictForm
from .models import training_testing, predict
import csv
from django.contrib import messages
from io import TextIOWrapper
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import joblib
import numpy as np 
import pandas as pd
from .pemodelan import split_data, model_xgboost, mean_absolute_percentage_error, accuracy

# Views Prediksi Padi

# prediksi dari input
def prediksi_input(request):
    prov = training_testing.objects.values_list('provinsi','kode_provinsi').distinct()
    prediksi_form = PredictForm(request.POST or None)
    df = None
    if request.method == 'POST':
        prediksi_form = PredictForm(request.POST)
        if prediksi_form.is_valid():
            provinsi = prediksi_form.cleaned_data.get('provinsi')
            kode_provinsi = prediksi_form.cleaned_data.get('kode_provinsi')
            bulan_tahun = prediksi_form.cleaned_data.get('bulan_tahun')
            luas_panen = prediksi_form.cleaned_data.get('luas_panen')
            produktivitas = prediksi_form.cleaned_data.get('produktivitas')
            curah_hujan = prediksi_form.cleaned_data.get('curah_hujan')
            hari_hujan = prediksi_form.cleaned_data.get('hari_hujan')

            # print("Data Provinsi:", provinsi)
            # print("Kode Provinsi:", kode_provinsi)

            data = {
                'provinsi': provinsi,
                'kode_provinsi': kode_provinsi,
                'bulan_tahun': bulan_tahun,
                'luas_panen': luas_panen,
                'produktivitas': produktivitas,
                'curah_hujan': curah_hujan,
                'hari_hujan': hari_hujan,
                'produksi':None,
            }

            df = pd.DataFrame(data, index=[0])
            var_input = df[['kode_provinsi', 'luas_panen', 'produktivitas', 'curah_hujan','hari_hujan']]

            # prediksi dengan xgboost
            xgb_jl = joblib.load('prediksi_padi/model_ml/xgb_joblib.joblib')
            prediksi = xgb_jl.predict(var_input)
            df['produksi'] = prediksi.round(2)
            print(df)

            # Simpan data ke dalam database
            for index, row in df.iterrows():
                prediksi_data = predict(
                    provinsi=row['provinsi'],
                    kode_provinsi=row['kode_provinsi'],
                    bulan_tahun=row['bulan_tahun'],
                    luas_panen=row['luas_panen'],
                    produktivitas=row['produktivitas'],
                    curah_hujan=row['curah_hujan'],
                    hari_hujan=row['hari_hujan'],
                    produksi=row['produksi']
                )
                prediksi_data.save()
            messages.success(request, 'Data berhasil diunggah')
        else:
            messages.error(request, 'Data tidak sesuai')
    else:
         post_form = UploadFileForm(request.POST)
    context = {
        'title':'Data Padi Prediksi Input',
        'prediksi_css':'prediksi/css/styles.css',
        'pred_form':prediksi_form,
        'provinsi':prov,
        'hasil_pred':df['produksi'][0] if df is not None else None,
    }
    
    return render(request, 'prediksi/prediksi.html', context)

# mendowload file csv hasil prediksi 
def export_csv_pred(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data_prediksi_padi.csv"'

    writer = csv.writer(response)
    writer.writerow(['id','provinsi','kode_provinsi','bulan_tahun','luas_panen','produktivitas','curah_hujan','hari_hujan','prediksi_produksi'])

    # data 
    data = predict.objects.all()
    prediksi = pd.DataFrame(data.values())
    # data_unduh = prediksi.values_list('provinsi','kode_provinsi','bulan_tahun','luas_panen','produktivitas','curah_hujan','hari_hujan','prediksi_produksi')
    data_unduh = prediksi.to_numpy()
    for hasil in data_unduh:
        writer.writerow(hasil)

    return response

# menampilkan grafik data prediksi per provinsi 
def tampil_grafik_pred(request,nama_provinsi):
    # data training & testing
    data_traintest = training_testing.objects.all()
    pred_traintest = model_xgboost(data_traintest.values())

    # prediksi data baru 
    data = predict.objects.all()
    xgb_jl = joblib.load('prediksi_padi/model_ml/xgb_joblib.joblib')
    df = pd.DataFrame(data.values())
    var_input = df[['kode_provinsi', 'luas_panen','produktivitas','curah_hujan','hari_hujan']]

    # prediksi dengan xgboost
    prediksi = xgb_jl.predict(var_input)

    # update kolom produksi dengan data hasil prediksi
    for i, data_padi in enumerate(data,):
        data_padi.produksi = prediksi[i]
    predict.objects.bulk_update(data, ['produksi'])

    # mengambil data hasil prediksi 
    data_hasil = predict.objects.filter(provinsi=nama_provinsi)

    # filter provinsi
    nama_prov = df['provinsi'].unique()
    prov = nama_provinsi
    filter_data = df[df['provinsi'] == nama_provinsi ]
    data_produksi = list(filter_data['produksi'])
    print(data_produksi)

    # filter data training untuk mape & akurasi
    filter_data_train = pred_traintest[pred_traintest['provinsi'] == nama_provinsi]

    # menghitung nilai mape & akurasi
    mape = mean_absolute_percentage_error(filter_data_train['produksi'],filter_data_train['prediksi_produksi'])
    akurasi = accuracy(mean_absolute_percentage_error(filter_data_train['produksi'],filter_data_train['prediksi_produksi']))
    
    context = {
        'title':'Hasil Prediksi Padi',
        'prediksi_css':'prediksi/css/styles.css',
        'data_hasil': data_hasil,
        'nama_prov':nama_prov,
        'prov':prov,
        'data_prediksi':data_produksi,
        'nilai_mape':mape,
        'nilai_akurasi':akurasi
    }
    return render(request, 'prediksi/hasil_pred.html', context)

# menampilkan data hasil prediksi
def hasil_pred(request):
    # data training & testing
    data_traintest = training_testing.objects.all()
    pred_traintest = model_xgboost(data_traintest.values())

    # prediksi data baru 
    data = predict.objects.all()
    xgb_jl = joblib.load('prediksi_padi/model_ml/xgb_joblib.joblib')
    df = pd.DataFrame(data.values())
    var_input = df[['kode_provinsi','luas_panen','produktivitas','curah_hujan','hari_hujan']]

    # prediksi dengan xgboost
    prediksi = xgb_jl.predict(var_input)

    # prediksi dengan xgboost 
    for i, data_padi in enumerate(data,):
        data_padi.produksi = prediksi[i]
    predict.objects.bulk_update(data, ['produksi'])

    # mengambil data hasil prediksi 
    data_hasil = predict.objects.all()
    df_hasil = pd.DataFrame(data_hasil.values())

    # menghitung mape dan akurasi 
    mape = mean_absolute_percentage_error(pred_traintest['produksi'],pred_traintest['prediksi_produksi'])
    akurasi = accuracy(mean_absolute_percentage_error(pred_traintest['produksi'],pred_traintest['prediksi_produksi']))

    nama_prov = df_hasil['provinsi'].unique()
    # kondervsi ke tipe datetimelike
    df_hasil['bulan_tahun'] = pd.to_datetime(df_hasil['bulan_tahun'])
    # mengelompokkan berdasarkan bulan dan hitung total produksi 
    df_hasil['bulan_tahun'] = df_hasil['bulan_tahun'].dt.to_period('M')
    data_prediksi = list(df_hasil.groupby('bulan_tahun')['produksi'].sum())
    print(df_hasil)
    print(data_prediksi)
  
    context = {
        'title':'Hasil Prediksi Padi',
        'prediksi_css':'prediksi/css/styles.css',
        'data_hasil': data_hasil,
        'nama_prov':nama_prov,
        'data_prediksi':data_prediksi,
        'nilai_mape':mape,
        'nilai_akurasi':akurasi
    }
    # print(context)
    return render(request, 'prediksi/hasil_pred.html', context)

# menampilkan data hasil upload data prediksi baru
def data_pred(request):
    data = predict.objects.all()
    p = Paginator(data,10)
    page = request.GET.get('page',1)
    p = Paginator(data, 10)
    try :
        hasil_data = p.page(page)
    except PageNotAnInteger:
        hasil_data = p.page(1)
    except EmptyPage:
        hasil_data = p.page(p.num_pages)
    context = {
        'title':'Data Prediksi Padi Upload',
        'prediksi_css':'prediksi/css/styles.css',
        'pagination':hasil_data,
    }           
    return render(request, 'prediksi/data_pred.html', context)

# memasukkan dari file csv ke database Testing
def handle_uploaded_file_pred(data_clean):
    result_data_save = []
    for row in data_clean:
        predict.objects.create(
            provinsi = row['provinsi'],
            kode_provinsi = row['kode_provinsi'],
            bulan_tahun = row['bulan_tahun'],
            luas_panen = row['luas_panen'],
            produktivitas = row['produktivitas'],
            # produksi = row['produksi'], ## variabel target
            curah_hujan = row['curah_hujan'],
            hari_hujan = row['hari_hujan'],
            )
        result_data_save.append(row)   
    return result_data_save

# cleaning data Prediksi
def clean_data_csv_pred(file):
    result_clean_data = []
    required_column = ['\ufeffprovinsi', 'kode_provinsi', 'bulan_tahun', 'luas_panen', 'produktivitas','produksi', 'curah_hujan', 'hari_hujan']
    with TextIOWrapper(file, encoding='utf-8') as file_wrapper:
        reader = csv.DictReader(file_wrapper, delimiter=';')
        for row in reader:
             # Membersihkan karakter BOM pada kunci 'provinsi'
            if all(col in row for col in required_column):
                cleaned_provinsi = row.pop('\ufeffprovinsi', None) if '\ufeffprovinsi' in row else row.get('provinsi')
                row['provinsi'] = cleaned_provinsi

                row['bulan_tahun'] = datetime.strptime(row['bulan_tahun'], '%m/%d/%Y').strftime('%Y-%m-%d')
                row['kode_provinsi'] = int(row['kode_provinsi'].replace(' ','').replace('.','').replace(',','.'))
                row['luas_panen'] = float(row['luas_panen'].replace(' ','').replace('.','').replace(',','.'))
                row['produktivitas'] = float(row['produktivitas'].replace(' ','').replace('.','').replace(',','.'))
                # row['produksi'] = float(row['produksi'].replace(' ','').replace('.','').replace(',','.'))
                row['curah_hujan'] = float(row['curah_hujan'].replace(' ','').replace('.','').replace(',','.'))
                row['hari_hujan'] = float(row['hari_hujan'].replace(' ','').replace('.','').replace(',','.'))

                result_clean_data.append(row)
            else:
                return None
    return result_clean_data

# upload data prediksi padi baru 
def up_data_pred(request):
    post_form = UploadFileForm(request.POST, request.FILES)
    if request.method == "POST":
        if post_form.is_valid():
            data_clean = clean_data_csv_pred(request.FILES["data_csv"])
            if data_clean is not None:
                data = handle_uploaded_file_pred(data_clean)
                # messages.success(request, 'Data berhasil diunggah')
                return redirect('prediksi_padi:data_pred')
            else:
                messages.error(request, 'Data Tidak Sesuai')
        else:
            messages.error(request, 'Data Tidak Sesuai')
    else:
        post_form = UploadFileForm(request.POST, request.FILES)
    context = {
        'title':'Data Padi Prediksi Baru',
        'prediksi_css':'prediksi/css/styles.css',
        'data_form':post_form,
    }
    return render(request, 'prediksi/load_data_prediksi.html', context)

################# Data Training #######################
# mendowload file csv hasil prediksi 
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data_prediksi_padi.csv"'

    writer = csv.writer(response)
    writer.writerow(['id','provinsi','kode_provinsi','bulan_tahun','luas_panen','produktivitas','curah_hujan','hari_hujan','prediksi_produksi'])

    # data 
    data = training_testing.objects.all()
    prediksi = model_xgboost(data.values())
    # data_unduh = prediksi.values_list('provinsi','kode_provinsi','bulan_tahun','luas_panen','produktivitas','curah_hujan','hari_hujan','prediksi_produksi')
    data_unduh = prediksi.to_numpy()
    for hasil in data_unduh:
        writer.writerow(hasil)

    return response

# menampilkan grafik per provinsi 
def tampil_grafik(request,provinsi):

    # mengambil data dan memprediksi
    data = training_testing.objects.all()
    prediksi = model_xgboost(data.values())

    data_hasil = prediksi[prediksi['provinsi'] == provinsi]

    # filter provinsi
    nama_prov = prediksi['provinsi'].unique()
    prov = provinsi
    filter_data = prediksi[prediksi['provinsi'] == provinsi ]
    data_produksi = list(filter_data['produksi'])
    data_prediksi = list(filter_data['prediksi_produksi'])

    # menghitung nilai mape & akurasi
    mape = mean_absolute_percentage_error(filter_data['produksi'],filter_data['prediksi_produksi'])
    akurasi = accuracy(mean_absolute_percentage_error(filter_data['produksi'],filter_data['prediksi_produksi']))
    
    context = {
        'title':'Hasil Prediksi Padi',
        'prediksi_css':'prediksi/css/styles.css',
        'data_hasil': data_hasil,
        'nama_prov':nama_prov,
        'prov':prov,
        'data_produksi':data_produksi,
        'data_prediksi':data_prediksi,
        'nilai_mape':mape,
        'nilai_akurasi':akurasi
    }
    return render(request, 'prediksi/hasil.html', context)

# menampilkan data hasil prediksi
def hasil(request):

    # mengambil data dan memprediksi
    data = training_testing.objects.all()
    prediksi = model_xgboost(data.values())

    # menghitung nilai mape & akurasi
    mape = mean_absolute_percentage_error(prediksi['produksi'],prediksi['prediksi_produksi'])
    akurasi = accuracy(mean_absolute_percentage_error(prediksi['produksi'],prediksi['prediksi_produksi']))

    # filter nama provinsi
    nama_prov = prediksi['provinsi'].unique()

    # kondervsi ke tipe datetimelike
    prediksi['bulan_tahun'] = pd.to_datetime(prediksi['bulan_tahun'])
    # mengelompokkan berdasarkan bulan dan hitung total produksi dan prediksi
    prediksi['bulan_tahun'] = prediksi['bulan_tahun'].dt.to_period('M')
    data_produksi = list(prediksi.groupby('bulan_tahun')['produksi'].sum())
    data_prediksi = list(prediksi.groupby('bulan_tahun')['prediksi_produksi'].sum())

    print(data_produksi)
    context = {
        'title':'Hasil Prediksi Padi',
        'prediksi_css':'prediksi/css/styles.css',
        'data_hasil': prediksi,
        'nama_prov':nama_prov,
        'data_produksi':data_produksi,
        'data_prediksi':data_prediksi,
        'nilai_mape':mape,
        'nilai_akurasi':akurasi
    }
    return render(request, 'prediksi/hasil.html', context)

# menampilkan data hasil upload data training
def data(request):
    data = training_testing.objects.all()
    p = Paginator(data,10)
    page = request.GET.get('page',1)
    p = Paginator(data, 10)
    try :
        hasil_data = p.page(page)
    except PageNotAnInteger:
        hasil_data = p.page(1)
    except EmptyPage:
        hasil_data = p.page(p.num_pages)
    context = {
        'title':'Data Training Padi Upload',
        'prediksi_css':'prediksi/css/styles.css',
        'pagination':hasil_data,
    }           
    return render(request, 'prediksi/data.html', context)

# memasukkan dari file csv ke database 
def handle_uploaded_file(data_clean):
    result_data_save = []
    for row in data_clean:
        training_testing.objects.create(
            provinsi = row['provinsi'],
            kode_provinsi = row['kode_provinsi'],
            bulan_tahun = row['bulan_tahun'],
            luas_panen = row['luas_panen'],
            produktivitas = row['produktivitas'],
            produksi = row['produksi'], ## variabel target
            curah_hujan = row['curah_hujan'],
            hari_hujan = row['hari_hujan'],
            )
        result_data_save.append(row)   
    return result_data_save

# cleaning data Training
def clean_data_csv(file):
    result_clean_data = []
    required_column = ['\ufeffprovinsi', 'kode_provinsi', 'bulan_tahun', 'luas_panen', 'produktivitas','produksi', 'curah_hujan', 'hari_hujan']
    with TextIOWrapper(file, encoding='utf-8') as file_wrapper:
        reader = csv.DictReader(file_wrapper, delimiter=';')
        for row in reader:
            # Membersihkan karakter pada kunci 'provinsi'
            if all(col in row for col in required_column):
                cleaned_provinsi = row.pop('\ufeffprovinsi', None) if '\ufeffprovinsi' in row else row.get('provinsi')
                row['provinsi'] = cleaned_provinsi

                row['bulan_tahun'] = datetime.strptime(row['bulan_tahun'], '%m/%d/%Y').strftime('%Y-%m-%d')
                row['kode_provinsi'] = int(row['kode_provinsi'].replace(' ','').replace('.','').replace(',','.'))
                row['luas_panen'] = float(row['luas_panen'].replace(' ','').replace('.','').replace(',','.'))
                row['produktivitas'] = float(row['produktivitas'].replace(' ','').replace('.','').replace(',','.'))
                row['produksi'] = float(row['produksi'].replace(' ','').replace('.','').replace(',','.'))
                row['curah_hujan'] = float(row['curah_hujan'].replace(' ','').replace('.','').replace(',','.'))
                row['hari_hujan'] = float(row['hari_hujan'].replace(' ','').replace('.','').replace(',','.'))

                result_clean_data.append(row)
            else:
                return None
    return result_clean_data
 
# upload file csv ke database
def up_data(request):
    post_form = UploadFileForm(request.POST, request.FILES)
    if request.method == "POST":
        if post_form.is_valid():
            data_clean = clean_data_csv(request.FILES["data_csv"])
            if data_clean is not None:
                data = handle_uploaded_file(data_clean)
                # messages.success(request, 'Data berhasil diunggah')
                return redirect('prediksi_padi:data')
            else:
                messages.error(request, 'Data tidak sesuai')
        else:
            messages.error(request, 'Data tidak sesuai')
    else:
        post_form = UploadFileForm(request.POST, request.FILES)
    context = {
        'title':'Data Padi Training',
        'prediksi_css':'prediksi/css/styles.css',
        'data_form':post_form,
    }
    return render(request, 'prediksi/load_data.html', context)
    

