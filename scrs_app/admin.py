from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *
# Register your models here.

class CustomerAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['cust_user', 'cust_mobile', 'cust_address', 'cust_locality', 'cust_city', 'cust_state', 'cust_pincode']
    list_per_page = 20
    search_fields = ('cust_user__username', 'cust_mobile', 'cust_address', 'cust_locality', 'cust_city', 'cust_state', 'cust_pincode')
admin.site.register(Customer,CustomerAdmin)

class Court_bookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'customer_name', 'customer_phone', 'date', 'start', 'end', 'court', 'price', 'payment', 'turf', 'is_booked', 'booking_date', 'payment_status']
    list_per_page = 20
admin.site.register(Court_booking,Court_bookingAdmin)