from django.urls import path
from . import views

app_name = "prediksi_padi"
urlpatterns = [
    path('download_hasil/', views.export_csv, name='export_csv'),
    path('download_hasil_pred/', views.export_csv_pred, name='export_csv_pred'),
    path("hasil_testing/<provinsi>/", views.tampil_grafik, name="hasil_filter"),
    path("hasil_testing/", views.hasil, name="hasil"),
    path("hasil_pred/<nama_provinsi>/",views.tampil_grafik_pred,name="hasil_pred_filter"),
    path("hasil_pred/",views.hasil_pred,name="hasil_pred"),
    path("data_pred/", views.data_pred, name="data_pred"),
    path("data/", views.data, name="data"),
    path("pred_input/", views.prediksi_input, name="pred_input"),
    path("load_data_pred/",views.up_data_pred, name="load_data_pred"),
    path("load_data/", views.up_data, name="load_data"),
]