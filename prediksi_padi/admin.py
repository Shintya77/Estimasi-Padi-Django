from django.contrib import admin

# Register your models here.
from .models import(training_testing,predict)
admin.site.register(training_testing)
admin.site.register(predict)