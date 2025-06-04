from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user__first_name', 'user__last_name', 'user__email', 'validation_code','is_validated']
    search_fields = ['user', 'is_validated']
