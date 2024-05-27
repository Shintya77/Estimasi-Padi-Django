# Generated by Django 5.0.2 on 2024-02-27 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='testing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provinsi', models.CharField(max_length=50)),
                ('kode_provinsi', models.IntegerField()),
                ('bulan_tahun', models.DateField()),
                ('luas_panen', models.FloatField()),
                ('produktivitas', models.FloatField()),
                ('curah_hujan', models.FloatField()),
                ('hari_hujan', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='training',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provinsi', models.CharField(max_length=50)),
                ('kode_provinsi', models.IntegerField()),
                ('bulan_tahun', models.DateField()),
                ('luas_panen', models.FloatField()),
                ('produktivitas', models.FloatField()),
                ('produksi', models.FloatField()),
                ('curah_hujan', models.FloatField()),
                ('hari_hujan', models.IntegerField()),
            ],
        ),
    ]