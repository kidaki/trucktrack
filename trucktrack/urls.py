from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from main.views import *

urlpatterns = patterns('',

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^logout/$',ExitView.as_view()),
    
    url(r'^$',login_required(IndexView.as_view())),
    
    url(r'^company/add/$',login_required(CompanyFormView.as_view())),
    url(r'^company/edit/(?P<id>\d+)/$',login_required(CompanyFormView.as_view())),
    url(r'^company/view/(?P<id>\d+)/$',login_required(CompanyView.as_view())),
    url(r'^company/delete/(?P<id>\d+)/$',login_required(CompanyDeleteView.as_view())),
    url(r'^companies/$',login_required(CompaniesView.as_view())),
    
    url(r'^driver/add/$',login_required(DriverFormView.as_view())),
    url(r'^driver/edit/(?P<id>\d+)/$',login_required(DriverFormView.as_view())),
    url(r'^driver/view/(?P<id>\d+)/$',login_required(DriverView.as_view())),
    url(r'^drivers/$',login_required(DriversView.as_view())),
    
    url(r'^trip/add/$',login_required(TripFormView.as_view())),
    url(r'^trip/edit/(?P<id>\d+)/$',login_required(TripFormView.as_view())),
    url(r'^trip/view/(?P<id>\d+)/$',login_required(TripView.as_view())),
    url(r'^trip/delete/(?P<id>\d+)/$',login_required(TripDeleteView.as_view())),
    url(r'^trip/invoice/(?P<trip_id>\d+)/$',login_required(InvoiceFormView.as_view())),
    url(r'^trips/$',login_required(TripsView.as_view())),
    
    url(r'^invoices/$',login_required(InvoicesView.as_view())),
    url(r'^invoices/sent/',login_required(InvoicesSentView.as_view())),
    url(r'^invoices/(?P<month>\w+)/$',login_required(InvoicesView.as_view())),
    url(r'^invoice/edit/(?P<invoice_id>\d+)/$',login_required(InvoiceFormView.as_view())),
    url(r'^invoice/delete/(?P<id>\d+)/$',login_required(InvoiceDeleteView.as_view())),
    url(r'^invoice/reactivate/(?P<id>\d+)/$',login_required(InvoiceReactivateView.as_view())),
    url(r'^invoice/print/(?P<id>\d+)/$',login_required(InvoicePrintView.as_view())),
    url(r'^invoice/pay/(?P<id>\d+)/$',login_required(InvoicePayView.as_view())),
    url(r'^invoice/pay/(?P<id>\d+)/(?P<payment_id>\d+)/$',login_required(InvoicePayView.as_view())),
    url(r'^invoice/sent/(?P<id>\d+)/$',login_required(InvoiceSentView.as_view())),
    
    url(r'^invoice/status/(?P<id>\d+)/$',login_required(InvoiceStatusView.as_view())),
    url(r'^invoice/view/(?P<id>\d+)/$',login_required(InvoiceView.as_view())),
    
    url(r'^profile/$',ProfileView.as_view()),
    url(r'^exit/$',ExitView.as_view()),
    url(r'^tsadmin/', include(admin.site.urls)),
    
)
