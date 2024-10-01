from django.contrib import admin
from .models import *

# Register your models here.


class KuponAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'active', 'value')


admin.site.register(MyUser)
admin.site.register(Transaction)
admin.site.register(Kupon,KuponAdmin)
admin.site.register(Bank)
admin.site.register(Credit)