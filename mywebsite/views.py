from multiprocessing import context
from unicodedata import name
from django.shortcuts import render

# Views MyWebsite
def index(request):
    context = {
        'title':'Sistem Estimasi Produksi Padi',
    }
    return render(request, 'index.html', context)