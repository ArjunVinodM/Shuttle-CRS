from django.urls import path
from . import views
from . views import *

urlpatterns = [
    # path('pay/<str:price>/<str:turf>', views.newhome, name='pay'),
    path('payment_done', views.payment_done, name='payment_done'),
    path('payment_cancelled', views.payment_cancelled, name='payment_cancelled'),
    path('', Index.as_view(), name='index'),
    path('login_page', Login.as_view(), name='login_page'),
    path('register', Register.as_view(), name='register'),
    path('registration', Register.as_view(), name='registration'),
    path('login', Login.as_view(), name='login'),
    path('home', Home.as_view(), name='home'),
    path('base', Base.as_view(), name='base'),
    path('admin', Admin.as_view(), name='admin'),
    path('book_court', Book.as_view(), name='book_court'),
    path('book', Bookcourtview.as_view(), name="book"),
    path('booking_court_view/<int:court_id>', Bookcourtview.as_view(), name='booking_court_view'),
    # path('get_existing_bookings/', views.get_existing_bookings, name='get_existing_bookings'),
    path('user_profile', UserProfile.as_view(), name='user_profile'),
    path('user_book_history', UserBookHistory.as_view(), name='user_book_history'),
    path('about_page', About.as_view(), name="about_page"),
    path('update_profile/<int:user_id>', UserProfile.as_view(), name="update_profile"),
    path('pass_change', PasswordChange.as_view(), name='pass_change'),
    path('user_pass_change', PasswordChange.as_view(), name='user_pass_change'),
    path('logout', Logout.as_view(), name='logout'),   
    path('cancel_booking/<int:booking_id>', CourtCancel.as_view(), name='cancel_booking'),
    path('forgot_page', ForgotPassword.as_view(), name='forgot_page'),
    path('forgot', ForgotPassword.as_view(), name='forgot'),
    path('terms', TermsAndConditions.as_view(), name='terms'),
    path('cancellation', CancellationAndPolicy.as_view(), name='cancellation'),

     
    ]