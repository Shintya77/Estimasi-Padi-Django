from django import forms

class UploadFileForm(forms.Form):
    data_csv = forms.FileField(
        widget = forms.FileInput(
              attrs = {
                'class':'custom-file-input',
                'accept':'text/csv'
            }
        )
    )

class PredictForm(forms.Form):
    provinsi = forms.CharField(
        widget= forms.TextInput(
            attrs= {
                'class':'custom-select mr-sm-',
            }
        )
    )
    kode_provinsi = forms.IntegerField(
        widget= forms.NumberInput(
            attrs= {
                'class':'custom-select mr-sm-',
            }
        )
    )
    bulan_tahun = forms.DateField(
        widget= forms.DateInput(
            attrs= {
                'class':'form-control',
                'type': 'date',

               
            }
            
        )
    )
    #  bulan_tahun = forms.DateField(
    #     widget= forms.SelectDateWidget(
    #         years = range(2018,2029,1),
    #         attrs= {
    #             'class':'form-control col-sm-2',
    #              'style': 'display: inline-block;', 
               
    #         }
            
    #     )
    # )
    luas_panen = forms.FloatField(
        widget= forms.NumberInput(
            attrs= {
                'class':'form-control',
                'placeholder':'Luas Panen'
            }
        )
    )  
    produktivitas = forms.FloatField(
         widget= forms.NumberInput(
            attrs= {
                'class':'form-control',
                'placeholder':'Produktivitas'
            }
        )
    )
    curah_hujan = forms.FloatField(
         widget= forms.NumberInput(
            attrs= {
                'class':'form-control',
                'placeholder':'Curah Hujan'
            }
        )
    )
    hari_hujan = forms.IntegerField(
         widget= forms.NumberInput(
            attrs= {
                'class':'form-control',
                'placeholder':'Hari Hujan'
            }
        )
    )
