from re import T
from django.db import models

# Create your models here.
class training_testing(models.Model):
    provinsi = models.CharField(max_length=50)
    kode_provinsi = models.IntegerField()
    bulan_tahun = models.DateField()
    luas_panen = models.FloatField()
    produktivitas = models.FloatField()
    produksi = models.FloatField()
    curah_hujan = models.FloatField()
    hari_hujan = models.IntegerField()

    def __str__(self):
        return f"{self.provinsi} - {self.bulan_tahun}"

class predict(models.Model):
    provinsi = models.CharField(max_length=50)
    kode_provinsi = models.IntegerField()
    bulan_tahun = models.DateField()
    luas_panen = models.FloatField()
    produktivitas = models.FloatField()
    curah_hujan = models.FloatField()
    hari_hujan = models.IntegerField()
    produksi = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.provinsi} - {self.bulan_tahun}"
