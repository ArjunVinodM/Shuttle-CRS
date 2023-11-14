from django.db import models
from django.contrib.auth.models import User
from image_cropping import ImageRatioField


# Create your models here.

class Customer(models.Model):
  cust_user = models.ForeignKey(User, on_delete=models.CASCADE)
  cust_mobile = models.CharField(max_length=10, default=10)
  cust_address = models.CharField(max_length=255)
  cust_locality = models.CharField(max_length=55)
  cust_city = models.CharField(max_length=55)
  cust_state = models.CharField(max_length=55)
  cust_pincode = models.IntegerField(default=6)
  cust_image = models.ImageField(upload_to='image/')
  
  
class Court(models.Model):
    name = models.CharField(max_length=55)
    court_image = models.ImageField(upload_to='image/')
    price = models.DecimalField(max_digits=10, decimal_places = 2)
    is_active = models.BooleanField(default=True)
    country = models.ForeignKey('cities_light.Country', on_delete=models.SET_NULL, null=True, blank=True) 
    city = models.ForeignKey('cities_light.City', on_delete=models.SET_NULL, null=True, blank=True)
  
class Court_booking(models.Model):
    INITIATED = 'Initiated'
    SUCCESS = 'Success'
    FAILED = 'Failed'
    
    PAYMENT_STATUS_CHOICES = [
        (INITIATED, 'Initiated'),
        (SUCCESS, 'Success'),
        (FAILED, 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=255)
    date = models.DateField()
    start = models.TimeField()
    end = models.TimeField()
    court = models.IntegerField()
    price = models.FloatField()
    payment = models.CharField(max_length=10)
    turf = models.ForeignKey(Court, on_delete=models.CASCADE)
    is_booked = models.BooleanField(default=False)
    booking_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(choices=PAYMENT_STATUS_CHOICES, max_length=20, default='INITIATED')
    



    