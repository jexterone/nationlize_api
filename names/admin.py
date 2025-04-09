from django.contrib import admin

from names.models import NameData


# Register your models here.

@admin.register(NameData)
class NameDataAdmin(admin.ModelAdmin):
    list_display = ['name','count','country',]
