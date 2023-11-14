from django.urls import path
# from . import views
from . views import *

urlpatterns = [
    # path('', views.base, name='base')
    path('logged_customers', Logcustomer.as_view(), name="logged_customers"),
    path('add_court', Courtadd.as_view(), name='add_court'),
    path('addcourt', Courtadd.as_view(), name='addcourt'),
    path('view_court', Courtview.as_view(), name="view_court"),
    path('court_status/<int:court_id>', Updatestatus.as_view(), name='court_status'),
    path('update_court/<int:update_id>', Courtupdate.as_view(), name='update_court'),
    path('court_updation/<int:update_id>', Courtupdate.as_view(), name='court_updation'),
    path('delete_added_court', Courtdeleteview.as_view(), name='delete_added_court'),
    path('delete_court/<int:court_id>', Courtdelete.as_view(), name='delete_court'),
    path('booking_history', Bookinghistory.as_view(),name='booking_history'),
    path('successful_booking_history', SuccessfulHistory.as_view(), name='successful_booking_history'),
    path('initiated_booking_history', InitiatedHistory.as_view(), name='initiated_booking_history'),
    path('admin_logout', AdminLogout.as_view(), name='admin_logout'),
    path('delete_customer/<int:customer_id>', CustomerDelete.as_view(), name='delete_customer'),
    path('payment_status/<int:payment_id>', UpdatePayment.as_view(), name='payment_status'),
    path('cancel_court/<int:booking_id>', AdminCourtCancel.as_view(), name='cancel_court'),
]