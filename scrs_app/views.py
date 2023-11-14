import base64
import re
import uuid
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.contrib.auth.models import User, auth
from admin_app.forms import CityFilterForm, CountryCityForm
from . models import *
from datetime import datetime, timedelta
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
from twilio.rest import Client
from django.contrib import messages
from django.db.models import Sum
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
from django.db.models import Q
from . subfunction import *
from django.core.files.base import ContentFile


# import re

# Create your views here.
# def base(request):
#   return render(request, 'index.html')

# class Index(View):
#   def get(self,request):
#       return render(request, 'admin_home.html')

class Base(View):
    def get(self,request):
        if request.user.is_authenticated: 
            court = Court.objects.filter(is_active=True)
            user = request.user.id
            if user:
                city_search = CityFilterForm(request.GET)
                selected_city = None
                city_search_query = request.GET.get('city_search_query','')
                if city_search.is_valid():
                    selected_city = city_search.cleaned_data['city']
                    if selected_city:
                        court = court.filter(city=selected_city)
                if city_search_query:
                    court = court.filter(city__name__icontains=city_search_query)
                return render(request, 'base.html', {'city_search_query':city_search_query})
            else:
                return redirect('login_page')
        else:
            return redirect('login_page')

class Index(View):
    def get(self,request):
        return render(request, 'index.html')
    
class Register(View):
    def get(self,request):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            country_form = CountryCityForm()
            return render(request, 'registration.html',{'country_form':country_form})
    
    def post(self,request):
        mobile = request.POST.get('mobile')
        uname = request.POST.get('user_name')
        email = request.POST.get('email')
        log_pass = request.POST.get('log_pass')
        conlog_pass = request.POST.get('conlog_pass')

        if log_pass == conlog_pass:
            if Customer.objects.filter(cust_mobile = mobile).exists():
                messages.info(request, 'Sorry, Mobile number already exists')
                return redirect('register')
            elif User.objects.filter(username = uname).exists():
                messages.info(request, 'Sorry, Username already exists')
                return redirect('register')
            elif not User.objects.filter(email = email).exists():
                
                user = User.objects.create_user(first_name = request.POST.get('f_name'),
                                                last_name = request.POST.get('l_name'),
                                                email = email,
                                                username = uname,
                                                password = log_pass)
                user.save()
                
                cust_data = Customer(cust_mobile = mobile,
                                    cust_address = request.POST.get('address'),
                                    cust_locality = request.POST.get('locality'),
                                    cust_city = request.POST.get('city'),
                                    cust_state = request.POST.get('state'),
                                    cust_pincode = request.POST.get('pincode'),
                                    cust_image = request.FILES.get('profile_image'),
                                    cust_user = user)
                cust_data.save()
                
                message = render_to_string('email_template.html', {'user': user, 'cust_data': cust_data, 'log_pass': log_pass})
                
                plain_message = strip_tags(message)
                
                subject = 'Welcome to BADMINTON AIR PLAZA'
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

                # subject = 'Welcome to BADMINTON AIR PLAZA'
                # # message = 'Greetings ' +user.first_name +' '+user.last_name+',\nWe Thank you for registering in Badminton Air Plaza.\nHere is your login email,mobile and password:\nEmail:'+ user.email+'\nMobile: '+ cust_data.cust_mobile +'\nPassword: '+ log_pass +'\nKeep it secure.' 
                # recipient = request.POST['email']     #  recipient =request.POST["inputTagName"]
                # send_mail(subject, message ,settings.EMAIL_HOST_USER, [recipient])
                return redirect('login_page')
            else:
                messages.info(request, 'Sorry, Email already exists')
                return redirect('register')
        else:
            messages.info(request, 'Sorry, Password and Repeat password does not match.')
            return redirect('register')
        
class Login(View):
    def get(self,request):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return render(request, 'login.html')
    
    def post(self, request):
        email_mobile = request.POST.get('email_or_mobile')
        passw = request.POST.get('log_pass')
        user = None
        
        if '@' in email_mobile:
            user = User.objects.filter(email=email_mobile).first()
            if user:
                user = authenticate(username=user.username, password=passw)
                messages.info(request, 'Sorry, Password seems to be incorrect')
                if user and not user.check_password(passw):
                    user = None
                    return redirect('login_page')
            else:
                messages.info(request, 'Sorry, Email seems to be incorrect')
                return redirect('login_page')
        else:
            cust = Customer.objects.filter(cust_mobile=email_mobile).first()
            if cust:
                user = cust.cust_user
                user = authenticate(username=user.username, password=passw)
                messages.info(request, 'Sorry, Password seems to be incorrect')

                if user and not user.check_password(passw):
                    user = None 
                    return redirect('login_page') 
            else:
                messages.info(request, 'Sorry, Email or Mobile number seems to be incorrect')
                return redirect('login_page') 
            
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('admin')
            else:
                login(request, user)
            return redirect('home')
        else:
            return redirect('login_page')
        

class Home(View):
    def get(self,request):
        if request.user.is_authenticated: 
            court = Court.objects.filter(is_active=True)
            user = request.user.id
            if user:
                user_id = Customer.objects.filter(cust_user_id=user).first()
                city_search = CityFilterForm(request.GET)
                selected_city = None
                city_search_query = request.GET.get('city_search_query','')
                if city_search.is_valid():
                    selected_city = city_search.cleaned_data['city']
                    if selected_city:
                        court = court.filter(city=selected_city)
                if city_search_query:
                    court = court.filter(city__name__icontains=city_search_query)
                return render(request, 'home.html', {'court':court, 'user':user_id, 'selected_city':selected_city, 'city_search_query':city_search_query})
            else:
                return redirect('login_page')
        else:
            return redirect('login_page')
    
class Book(View):
    def get(self,request):
        if request.user.is_authenticated:
            court = Court.objects.all()
            return render(request, 'book_court.html', {'court': court})
        else:
            return redirect('login_page')
        
class PasswordChange(View):
    def get(self,request):
        if request.user.is_authenticated:
            user = request.user.id
            if user:
                user_id = Customer.objects.filter(cust_user_id=user).first()
                return render(request, 'change_password.html', {'user':user_id})
            else:
                return redirect('login_page')
        else:
            return redirect('login_page')
    
    def post(self, request):
        current_passw = request.POST.get('current_pass')
        new_passw = request.POST['password']
        repeat_passw = request.POST['cpassword']
        user = authenticate(username = request.user.username, password = current_passw)
        
        if repeat_passw == new_passw:
            if user is not None:
                user.set_password(new_passw)
                user.save()
                messages.success(request, 'Password has been changed successfully.')
                return redirect('pass_change')
            else:
                messages.info(request, 'Sorry, Current password is invalid please try again.')
                return redirect('pass_change')
        else:
            messages.info(request, 'Sorry, New password and Repeat password does not match.')
            return redirect('pass_change')

class Bookcourtview(View):
    def get(self,request,court_id):
        if request.user.is_authenticated:
            user = request.user.id
            if user:
                user_id = Customer.objects.filter(cust_user_id=user).first()
                court = Court.objects.filter(id=court_id).first()
                if court:
                    return render(request, 'book_court.html', {'court': court, 'user':user_id})
                else:
                    messages.info(request, 'unable to provide court please try after sometime')
                    return redirect('home')
            else:
                return redirect('login_page')
        else:
            return redirect('login_page')
    
    def post(self,request):
        user = request.user
        date = request.POST.get('date')
        start_time = request.POST.get('starttime')
        end_time = request.POST.get('endtime')
        court = request.POST.get('court')
        price = request.POST.get('price')
        turf = request.POST.get('turf')
        payment = request.POST.get('payment')
        starttime = datetime.strptime(start_time, '%H:%M').time()
        endtime = datetime.strptime(end_time, '%H:%M').time()
        turfid = Court.objects.filter(id=turf).first()
        if turfid:
            customer = Customer.objects.filter(cust_user = user).first()
            if customer:
                email=customer.cust_user.email
                mobile = customer.cust_mobile
                fname = customer.cust_user.first_name
                lname = customer.cust_user.last_name
                
                print(mobile)
                        
                existing_bookings = Court_booking.objects.filter(court=court, date=date, turf=turfid)
                for existing in existing_bookings:
                    if (existing.start <= starttime < existing.end) or \
                        (existing.start < endtime <= existing.end) or\
                            (starttime < existing.start and endtime > existing.end):
                        if not existing.payment_status == 'FAILED':
                            messages.info(request, ' Slot already booked. Please choose another slot or book another turf.')
                            return redirect(reverse('booking_court_view', kwargs={'court_id': turf}))
                if payment == 'offline':
                    Court_booking.objects.create(date = date,
                                                user = user,
                                                customer_name = fname +' '+ lname,
                                                customer_phone = mobile,
                                                start = start_time,
                                                end = end_time,
                                                court = court,
                                                price = price,
                                                turf = turfid,
                                                payment = payment,
                                                payment_status = "INITIATED",
                                                is_booked=True)
                    # subject = 'BADMINTON AIR PLAZA'
                    # message = 'Greetings ' +customer.cust_user.first_name +' '+customer.cust_user.last_name+',\nThank you for choosing to spend your valuable time to play a match at '+turfid.name+'.\nYour match has been sheduled on '+date+' From '+start_time+' to '+ end_time +' at court number '+ turf +' .Please ensure to reach '+turfid.name+' on time.\nGood Luck! to all players...'
                    # recipient = email 
                    # send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient])
                    
                    message = render_to_string('email_payment.html', {'customer': customer, 'turfid': turfid, 'date':date, 'start_time':start_time, 'end_time':end_time, 'court':court})
                        
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
                
                    account_sid = 'AC61e6b0246ee69ee8517ed5d6579e8679'
                    auth_token = '5e40ade16c088f65f05f38c0a6fe6661'
                    client = Client(account_sid, auth_token)
                    client.messages.create(body='Your booking has been done successfully', from_='whatsapp:+14155238886', to='whatsapp:+918921986803')
                
                    account_sid = 'AC61e6b0246ee69ee8517ed5d6579e8679'
                    auth_token = '5e40ade16c088f65f05f38c0a6fe6661'
                    client = Client(account_sid, auth_token)

                    message = client.messages.create(
                    body='Your booking has been done successfully',
                    from_='+12294145912',
                    to='+918921986803'
                    )

                    print(message.sid)
                    messages.success(request, "Slot booked successfully.")
                    return redirect('user_book_history')
                else:
                    host = request.get_host()
                    booking = Court_booking.objects.create(date = date,
                        user = user,
                        start = start_time,
                        customer_name = fname +' '+ lname,
                        customer_phone = mobile,
                        end = end_time,
                        court = court,
                        price = price,
                        turf = turfid,
                        payment = payment,
                        payment_status="FAILED",
                        is_booked=True)
                    paypal_dict = {
                    'business': settings.PAYPAL_RECEIVER_EMAIL,
                    'amount': price,
                    'item_name': turfid.name,
                    'invoice': str(uuid.uuid4()),
                    'currency_code': 'USD',
                    'notify_url': f'http://{host}{reverse("paypal-ipn")}',
                    'return_url': f'http://{host}{reverse("payment_done")}?id={booking.id}',
                    'cancel_return': f'http://{host}{reverse("payment_cancelled")}?id={booking.id}',
                    }
                    form = PayPalPaymentsForm(initial = paypal_dict)
                    print(form)
                    context = {'form':form,
                            'booking':booking,
                            'user':customer}
                    print(booking.id)
                    return render(request, 'paypal_booking.html', context)
            else:
                return redirect('home')
        else: 
            return redirect('login_page')


def payment_done(request):
    booking = request.GET.get('id')
    user = request.user.id
    if booking:
        Court_booking.objects.filter(id = booking).update(payment_status = "SUCCESS",
                                                        is_booked=True)
        
        court = Court_booking.objects.filter(id = booking).first()
        if court:
            user_id = Customer.objects.filter(cust_user_id=user).first()
            if user_id:
                email = user_id.cust_user.email
                        
                message = render_to_string('email_payment_online.html', {'court':court})      
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
                account_sid = 'AC61e6b0246ee69ee8517ed5d6579e8679'
                auth_token = '5e40ade16c088f65f05f38c0a6fe6661'
                client = Client(account_sid, auth_token)
                client.messages.create(body='Your booking has been done successfully', from_='whatsapp:+14155238886', to='whatsapp:+918921986803')
                
                account_sid = 'AC61e6b0246ee69ee8517ed5d6579e8679'
                auth_token = '5e40ade16c088f65f05f38c0a6fe6661'
                client = Client(account_sid, auth_token)

                message = client.messages.create(
                body='Your booking has been done successfully',
                from_='+12294145912',
                to='+918921986803'
                )
                messages.success(request, "Slot booked successfully.")                
                return redirect('user_book_history')
            else:
                return redirect('login_page')
        else:
            return redirect('home')
    else:
        return redirect('payment_cancelled')
        
def payment_cancelled(request):
    booking = request.GET.get('id')
    Court_booking.objects.filter(id = booking).update(payment_status = "FAILED",
                                                        is_booked=True)
    return redirect('home')  

class CourtCancel(View):
    def get(self, request, booking_id):
        user = request.user.id
        user_id = Customer.objects.filter(cust_user_id=user).first()
        if user_id:
            booking = Court_booking.objects.filter(id = booking_id).first()
            if booking:
                now_time = datetime.now()
                booking_time = datetime.combine(booking.date, booking.start)
                if now_time>=booking_time:
                    messages.info(request,'sorry, Cancellation is not allowed at this time.')
                    return redirect('user_book_history')
                else:
                    booking.payment_status = 'FAILED'
                    booking.save()
                    
                    email = user_id.cust_user.email
                        
                    message = render_to_string('cancel_payment_email.html', {'booking':booking})      
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
                    return redirect('user_book_history')
            else:
                return redirect('user_book_history')
        else:
            return redirect('login_page')
        
        

class UserProfile(View):
    def get(self,request):
        if request.user.is_authenticated:
            user = request.user.id
            if user:
                user_id = Customer.objects.filter(cust_user_id=user).first()
                if user_id:
                    return render(request, 'profile_view.html', {'user':user_id})  
                else:
                    return redirect('login_page') 
            else:
                return redirect('login_page') 
        else:
            return redirect('login_page') 
    
    def post(self,request,user_id): 
        update = Customer.objects.filter(id=user_id).first()
        if update:
            user = request.user
            
            fname = request.POST['u_fname']
            lname = request.POST['u_lname']
            email = request.POST['u_email']
            
            update.cust_mobile = request.POST.get('u_mobile')
            update.cust_address = request.POST.get('u_address')
            update.cust_locality = request.POST.get('u_locality')
            update.cust_city = request.POST.get('u_city')
            update.cust_state = request.POST.get('u_state')
            update.cust_pincode = request.POST.get('u_pincode')
            
            # update.cust_image = request.FILES.get('profile_image')
            base64_image = request.POST.get('cropped_image') 

            if base64_image and ';base64,' in base64_image:
                format, imgstr = base64_image.split(';base64,')
                if re.match('^[A-Za-z0-9+/]+[=]{0,2}$', imgstr): 
            
                    ext = format.split('/')[-1] 
                    data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext) 

                    update.cust_image = data 
            update.save()
    
            user.first_name = fname
            user.last_name = lname
            user.email = email
    
            user.save()
            
            return redirect('user_profile')
        else:
            return redirect('user_profile')
    
class UserBookHistory(View):
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user.id
            if user:
                user_id = Customer.objects.filter(cust_user_id=user).first()
                print(user)
                book_history = Court_booking.objects.filter(Q(user_id = user) & (Q(payment_status='SUCCESS') | Q(payment_status='INITIATED'))).order_by('-id')
                if book_history:
                    return render(request, 'book_history.html', {'book_history':book_history, 'user':user_id}) 
                else:
                    return render(request, 'empty_cart.html') 
            else:
                return redirect('login_page')    
        else:
            return redirect('login_page')
    
class About(View):
    def get(self,request):
        user = request.user.id
        user_id = Customer.objects.filter(cust_user_id=user).first()
        return render(request, 'about.html', {'user':user_id})  
    
class Logout(View):
    def get(self,request):
        auth.logout(request)
        request.session.flush()
        return redirect('/')            
    
class Admin(View):
    def get(self, request):
        if request.user.is_authenticated:
            # court = Court_booking.objects.all()
            reversed_court = Court_booking.objects.all().order_by('-id')
            # reversed_court = list(reversed(court))
            current_date = datetime.now()
            
            first_day = current_date.replace(day=1)
            last_day = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            income = Court_booking.objects.filter(date__range=[first_day, last_day], payment_status='SUCCESS').aggregate(total=Sum('price'))['total'] or 0
            
            year_first_day = current_date.replace(month=1, day=1)
            year_last_day = current_date.replace(month=12, day=31)
            
            yearly_income = Court_booking.objects.filter(date__range=[year_first_day, year_last_day], payment_status='SUCCESS').aggregate(total=Sum('price'))['total'] or 0 
            # aggregate used to apply a function or a list of function names to be executed along one of the axis of the dataframe.
            reversed_court_status = Court_booking.objects.filter(payment_status = 'SUCCESS').order_by('-id')
            # reversed_court_status = list(reversed(court_status))
            return render(request, 'admin_home.html', {'income':income, 'court':reversed_court, 'yearly_income':yearly_income, 'court_status':reversed_court_status})
        else:
            return redirect('login_page')

class ForgotPassword(View):
    def get(self, request):
        return render(request, 'forgotten_password.html')
    
    def post(self, request):
        email = request.POST.get('email')
        
        user = User.objects.filter(email=email).first()
        
        if user:
            generated_password = generate_password()
            user.set_password(generated_password)
            user.save()
            
            message = render_to_string('forgot_email.html', {'password':generated_password, 'user':user})      
            plain_message = strip_tags(message)
            
            subject = 'BADMINTON AIR PLAZA - password reset'
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
            messages.success(request,'New password sent to your mail')
            return redirect('login_page')
        else:
            messages.info(request,'Email does not exist')
            return redirect('forgot_page')
        
class TermsAndConditions(View):
    def get(self, request):
        user = request.user.id
        if user:
            user_id = Customer.objects.filter(cust_user_id=user).first()
            return render(request, 'terms_and_conditions.html', {'user':user_id})
        else:
            return render(request, 'terms_and_conditions.html')
    
class CancellationAndPolicy(View):
    def get(self, request):
        user = request.user.id
        if user:
            user_id = Customer.objects.filter(cust_user_id=user).first()
            return render(request, 'cancellation.html', {'user':user_id})
        else:
            return render(request, 'cancellation.html')
