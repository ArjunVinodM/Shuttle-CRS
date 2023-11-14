from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from admin_app.forms import CountryCityForm
from . models import *
from scrs_app.models import *
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, auth
from django.core.paginator import Paginator
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
from django.db.models import Q

class Logcustomer(View):
  def get(self, request):
    if request.user.is_authenticated:
        customer = Customer.objects.all().order_by('-id')
        context = {
            'customer':customer
        }
        return render(request, 'admin_customer.html', context)
    else:
        return redirect('login_page')
  
class Courtadd(View):
    def get(self,request):
        if request.user.is_authenticated:
            country_form = CountryCityForm()
            return render(request, 'admin_add_court.html', {'country_form':country_form})
        else:
            return redirect('login_page')
    
    def post(self,request):
        name = request.POST.get('court_name')
        price = request.POST.get('court_price')
        image = request.FILES.get('court_image')
        
        country_form = CountryCityForm(request.POST)
        if country_form.is_valid():
            selected_country = country_form.cleaned_data['country']
            selected_city = country_form.cleaned_data['city']
            if Court.objects.filter(name=name ).exists():
                messages.success(request, 'Court name already exists, Please choose another name')
                return redirect('addcourt')
            else:
                add_court = Court(name = name,
                                price = price,
                                court_image = image,
                                country = selected_country,
                                city = selected_city)
                add_court.save()
        messages.info(request,'New Turf has been added')
        return redirect('view_court')
    
    
class Courtview(View):
    def get(self,request):
        if request.user.is_authenticated:
            court = Court.objects.all().order_by('-id')
            return render(request, 'admin_view_court.html', {'court':court})
        else:
            return redirect('login_page')
    
class Updatestatus(View):
    def post(self,request,court_id):
        court = Court.objects.filter(id=court_id).first()
        
        if court:
            court_id = court.id
            current_date = datetime.now().date()
            
            if Court_booking.objects.filter(turf = court_id, date__gte = current_date).exists():
                messages.info(request, 'Currently Court cannot be moved to inactive state as it is already booked by a user.')
                return redirect('view_court')
            else:
                new_status = request.POST.get('status')
                if new_status == 'active':
                    court.is_active = True
                    court.save()
                    messages.success(request, 'Court is now active.')
                    return redirect('view_court')
                elif new_status == 'inactive':
                    court.is_active = False
                    court.save()
                    messages.success(request, 'Court is now inactive.')
                    return redirect('view_court')
                else:
                    messages.error(request, 'Invalid status update request.')
                    return redirect('view_court')   
        else:
            messages.error(request, 'Invalid court id selected')
            return redirect('view_court')           
            
class Courtupdate(View):
    def get(self,request,update_id):
        if request.user.is_authenticated:
            court = Court.objects.filter(id=update_id).first()
            return render(request, 'admin_update_court.html', {'court':court})
        else:
            return redirect('login_page')
    
    def post(self,request,update_id):
        update = Court.objects.filter(id=update_id).first()
        update.name = request.POST.get('court_name')
        update.price = request.POST.get('court_price')
        
        old = update.court_image
        new = request.FILES.get('court_image')
        
        if old != None and new == None:
            update.court_image = old
        else:
            update.court_image = new
            update.save()
            messages.success(request, 'Court updated successfully')
            return redirect('view_court')
    
class Courtdeleteview(View):
    def get(self,request):
        if request.user.is_authenticated:
            court = Court.objects.all()
            return render(request, 'admin_delete_court.html',{'court':court})
        else:
            return redirect('login_page')
    
    
class Courtdelete(View):  
    def get(self,request,court_id):
        if request.user.is_authenticated:
            court = Court.objects.filter(id=court_id).first()
            court.delete()
            messages.success(request, 'court removed successfully')
            return redirect('view_court')
        else:
            return redirect('login_page')
    
class Bookinghistory(View):
    def get(self,request):
        if request.user.is_authenticated:
            history = Court_booking.objects.filter((Q(payment_status='SUCCESS') | Q(payment_status='INITIATED'))).order_by('-id')

            return render(request,'admin_booking_history.html', {'history':history})
        else:
            return redirect('login_page')
    
class SuccessfulHistory(View):
    def get(self,request):
        if request.user.is_authenticated:
            successful = Court_booking.objects.filter(payment_status = 'SUCCESS')
            return render(request, 'admin_successful_booking.html', {'success':successful})
        else:
            return redirect('login_page')
    
class InitiatedHistory(View):
    def get(self,request):
        if request.user.is_authenticated:
            initiated = Court_booking.objects.filter(payment_status = 'INITIATED')
            return render(request, 'admin_booking_history.html', {'initiated':initiated})
        else:
            return redirect('login_page')

class UpdatePayment(View):
    def post(self,request,payment_id):
        initiate = Court_booking.objects.filter(id=payment_id).first()
        if initiate:
            new_status = request.POST.get('success')
            if new_status == 'SUCCESS':
                initiate.payment_status = 'SUCCESS'
                initiate.save()
                messages.info(request, 'Payment Received')
                return redirect('booking_history')
            else:
                messages.info(request, 'Failed')
                return redirect('booking_history')
        else:
            messages.info(request, 'Unable to fetch payment ID')
            return redirect('booking_history')
        
    
class CustomerDelete(View):
    def get(self,request,customer_id):
        if request.user.is_authenticated:
            customer = Customer.objects.filter(id = customer_id).first()
            if customer:
                user = customer.cust_user
                if user:
                    user.delete()    
                customer.delete()
                messages.success(request, 'Customer removed successfully')
                return redirect('logged_customers')
            else:
                messages.info(request, 'Customer not found')
                return redirect('logged_customers')
        else:
            return redirect('login_page')   
        
class AdminCourtCancel(View):
    def get(self,request, booking_id):
        bookings = Court_booking.objects.filter(id = booking_id).first()
        # user_id = bookings.user_id
        if bookings.user_id:
            user_email = bookings.user.email
            # user = User.objects.filter(id=user_id).first()
            # user_email = user.email
            print(user_email)
            now = datetime.now()
            book_cancel = datetime.combine(bookings.date, bookings.start)
            
            if now<=book_cancel:
                
                bookings.payment_status = 'FAILED'
                bookings.save()
                
                
                email = user_email
                print(email)
                    
                message = render_to_string('cancel_payment_email.html', {'booking':bookings})      
                plain_message = strip_tags(message)
                
                subject = 'BADMINTON AIR PLAZA'
                from_email = settings.EMAIL_HOST_USER
                to_email = email

                email = EmailMultiAlternatives(subject, plain_message, from_email, [to_email])
                email.attach_alternative(message, "text/html")

                with open("static/images/logo6.png", "rb") as f:
                    logo_data = f.read()
                    email_image = MIMEImage(logo_data)
                    email_image.add_header('Content-ID', '<logo>')
                    email.attach(email_image)

                    email.send()
                messages.success(request,'cancellation Successful')
                return redirect('booking_history')
            else:
                messages.success(request,'cancellation is not allowed at this moment')
                return redirect('booking_history')     
        else:
            messages.success(request,'cancellation is not allowed at this moment')
            return redirect('booking_history') 
    
class AdminLogout(View):
    def get(self,request):
        auth.logout(request)
        request.session.flush()
        return redirect('/') 