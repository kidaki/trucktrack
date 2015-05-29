from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth import logout
from django.http import HttpResponse,HttpResponseRedirect
from django.template.response import TemplateResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from main.models import *
from datetime import date,timedelta
from collections import OrderedDict
import operator




class IndexView(View):
    template = 'index.html'
    
    def get(self,request,*args,**kwargs):
        """
        Home page will have:
        unpaid invoices
        trips without invoices
        other things to come
        """
        company_volume_sales = {}
        six_months_ago = date.today()-timedelta(days = 6*30)
        for trip in Trip.objects.filter(pickup__isnull=False,pickup__date__range=(six_months_ago,date.today())):
            if trip.company.name in company_volume_sales:
                company_volume_sales[trip.company.name] += 1
            else:
                company_volume_sales[trip.company.name] = 1
        
        company_volume_sales = OrderedDict(sorted(company_volume_sales.items(),key=operator.itemgetter(1),reverse=True))
        volume_sales = OrderedDict()
        other_volume_sales = 0
        for company,volume in company_volume_sales.iteritems():
            if company_volume_sales.keys().index(company) < 5:
                volume_sales[company] = volume
            else:
                other_volume_sales += volume
        if other_volume_sales:
            volume_sales['Other'] = other_volume_sales
        
        
        
        ###
        ### I need to do this with annotate, or raw sql group by
        ###
        
        sales = {}
        sales['months'] = []
        sales['total'] = []
        months = ['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        for i in range(6):
            month = (date.today()-timedelta(days = i*30)).month
            name = months[month]
            total = sum([int(invoice.get_total()) for invoice in Invoice.objects.filter(date__month=month)])
            sales['months'].append(name)
            sales['total'].append(total)
        sales['months'].reverse()
        sales['total'].reverse()
        return TemplateResponse(request,self.template,{
            'active':'home',
            'sales':sales,
            'volume_sales':volume_sales,
            'invoices':Invoice.objects.filter(payment__isnull=True)
        })

class CompaniesView(View):
    template = 'company/companies.html'
    
    def get(self,request,*args,**kwargs):
        companies = Company.objects.all()
        
        search = request.session.get('companies_search')
        if search:
            companies = companies.filter(name__icontains=search)
        
        paginator = Paginator(companies,25)
        page = request.GET.get('page')
        try:
            companies = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            companies = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            companies = paginator.page(paginator.num_pages)

        return TemplateResponse(request,self.template,{
            'active':'company',
            'search':search,
            'companies':companies,
        })
    
    def post(self,request,*args,**kwargs):
        
        request.session['companies_search'] = request.POST.get('search')
        return HttpResponseRedirect('/companies/')

class CompanyFormView(View):
    template = 'company/company_form.html'
    
    def get(self,request,*args,**kwargs):
        company = Company.objects.get(id=kwargs['id']) if 'id' in kwargs else None
        form = CompanyForm(instance=company)
        return TemplateResponse(request,self.template,{
            'form':form,
            'active':'company',
        })
    
    def post(self,request,*args,**kwargs):
        company = Company.objects.get(id=kwargs['id']) if 'id' in kwargs else None
        form = CompanyForm(request.POST,instance=company)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect('/companies/')

class CompanyView(View):
    template = 'company/company_view.html'
    
    def get(self,request,*args,**kwargs):
        company = Company.objects.get(id=kwargs['id'])
        return TemplateResponse(request,self.template,{'company':company})

class CompanyDeleteView(View):
    
    def get(self,request,*args,**kwargs):
        """ This function will just mark the company deleted and return a redirect to companies """
        company = Company.objects.get(id=kwargs.get('id'))
        company.deleted = True
        company.save()
        
        return HttpResponseRedirect('/companies/')

class DriverFormView(View):
    template = 'driver/driver_form.html'
    
    def get(self,request,*args,**kwargs):
        driver = Driver.objects.get(id=kwargs['id']) if 'id' in kwargs else None
        form = DriverForm(instance=driver)
        return TemplateResponse(request,self.template,{'form':form})
    
    def post(self,request,*args,**kwargs):
        driver = Driver.objects.get(id=kwargs['id']) if 'id' in kwargs else None
        form = DriverForm(request.POST,instance=driver)
        if form.is_valid():
            driver = form.save()
        return HttpResponseRedirect('/driver/view/{0}'.format(driver.id))

class DriversView(View):
    template = 'driver/drivers.html'
    
    def get(self,request,*args,**kwargs):
        drivers = Driver.objects.all()
        
        search = request.session.get('drivers_search')
        if search:
            drivers = drivers.filter(name__icontains=search)
        
        paginator = Paginator(drivers,25)
        page = request.GET.get('page')
        try:
            drivers = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            drivers = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            drivers = paginator.page(paginator.num_pages)
        
        return TemplateResponse(request,self.template,{
            'drivers':drivers,
            'search':search
        })
    
    def post(self,request,*args,**kwargs):
        
        request.session['drivers_search'] = request.POST.get('search')
        return HttpResponseRedirect('/drivers/')

class DriverView(View):
    template = 'driver/driver_view.html'
    
    def get(self,request,*args,**kwargs):
        driver = Driver.objects.get(id=kwargs['id'])
        return TemplateResponse(request,self.template,{'driver':driver})
        
class TripFormView(View):
    template = 'trip/trip_form.html'
    def get(self,request,*args,**kwargs):
        trip = Trip.objects.get(id=kwargs['id']) if 'id' in kwargs else None
        form = TripForm(instance=trip)
        delivery_formset = DeliveryFormSet(instance=trip)
        pickup_formset = PickupFormSet(instance=trip)
        return TemplateResponse(request,self.template,{
            'form':form,
            'delivery_formset':delivery_formset,
            'pickup_formset':pickup_formset
        })
    
    def post(self,request,*args,**kwargs):
        trip = Trip.objects.get(id=kwargs['id']) if 'id' in kwargs else None
        form = TripForm(request.POST,instance=trip)
        if form.is_valid():
            trip = form.save()
            
            delivery_formset = DeliveryFormSet(request.POST,instance=trip)
            if delivery_formset.is_valid():
                delivery_formset.save()
            
            pickup_formset = PickupFormSet(request.POST,instance=trip)
            if pickup_formset.is_valid():
                pickup_formset.save()
            
            return HttpResponseRedirect('/trips/')
        return TemplateResponse(request,self.template,{
            'form':form,
            'delivery_formset':delivery_formset,
            'pickup_formset':pickup_formset
        })
      
class TripsView(View):
    template = 'trip/trips.html'
    
    def get(self,request,*args,**kwargs):
        # trips that have not been invoiced
        # trips today, yesterday, and the day before and then some filter option
        
        trips = Trip.objects.filter(deleted=False)
        
        # search and filters
        search = request.session.get('trips_search','')
        trips = trips.filter(Q(load_number__icontains=search) | Q(company__name__icontains=search))
        
        invoices = request.session.get('trips_invoices','all')
        queries = {
            'paid':Q(invoice__payment__isnull=False),
            'notpaid':Q(invoice__payment__isnull=True),
            'notinvoiced':Q(invoice__isnull=True)
        }
        if invoices != 'all':
            trips = trips.filter(queries[invoices])
            
        paginator = Paginator(trips,25)
        page = request.GET.get('page')
        try:
            trips = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            trips = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            trips = paginator.page(paginator.num_pages)
        
        return TemplateResponse(request,self.template,{
            'trips':trips,
            'search':search,
            'invoices':invoices,
        })
        
    def post(self,request,*args,**kwargs):
        
        invoices = request.POST.get('invoices')
        search = request.POST.get('search')

        request.session['trips_invoices'] = invoices
        request.session['trips_search'] = search
        
        return HttpResponseRedirect('/trips/')

class TripView(View):
    template = 'trip/trip_view.html'
    
    def get(self,request,*args,**kwargs):
        return TemplateResponse(request,self.template,{'trip':Trip.objects.get(id=kwargs['id'])})
    
class TripDeleteView(View):
    
    def get(self,request,*args,**kwargs):
        trip = Trip.objects.get(id=kwargs.get('id'))
        trip.deleted = True
        trip.save()
        
        return HttpResponseRedirect('/trips/')
    
class InvoicesView(View):
    template = 'invoice/invoices.html'
    def get(self,request,*args,**kwargs):
        months = (
            ('1','January'),
            ('2','February'),
            ('3','March'),
            ('4','April'),
            ('5','May'),
            ('6','June'),
            ('7','July'),
            ('8','August'),
            ('9','September'),
            ('10','October'),
            ('11','November'),
            ('12','December')
        ) # for select months in template

        invoices = Invoice.objects.filter(trip__deleted=False,deleted=False)
        
        month = request.session.get('invoice_month','all')
        payment = request.session.get('invoice_payment','all')
        sent = request.session.get('invoice_sent','all')
        search = request.session.get('invoice_search','')
        
        if month != 'all':
            invoices = invoices.filter(date__month=int(month))
        if payment != 'all':
            queries = {
                'paid':Q(payment__isnull=False,paidoff=True),
                'shortpaid':Q(payment__isnull=False,paidoff=False),
                'notpaid':Q(payment__isnull=True),
            }
            invoices = invoices.filter(queries[payment])
        if sent != 'all':
            invoices = invoices.filter(faxed_emailed={'sent':True,'notsent':False}[sent])
        if search:
            invoices = invoices.filter(trip__company__name__icontains=search)
        
        # check if there are unsent invoices.  This is used to hide the send/mark all buttons
        display_send_buttons = invoices.filter(faxed_emailed=False)
        
        return TemplateResponse(request,self.template,{
            'months':months,
            'month':month,
            'payment':payment,
            'search':search,
            'sent':sent,
            'display_send_buttons':display_send_buttons,
            'invoices':invoices,
        })
        
    def post(self,request,*args,**kwargs):
        """
        Handle post
        set session variables for easier filtering
        """
        # read post
        month = request.POST.get('month')
        payment = request.POST.get('payment')
        sent = request.POST.get('sent')
        search = request.POST.get('search')
        
        # session
        request.session['invoice_month'] = month
        request.session['invoice_payment'] = payment
        request.session['invoice_sent'] = sent
        request.session['invoice_search'] = search
        
        return HttpResponseRedirect('/invoices/')

class InvoicesSentView(View):
    
    def post(self,request,*args,**kwargs):
        for invoice_id in request.POST.getlist('sent'):
            invoice = Invoice.objects.get(id=invoice_id)
            invoice.faxed_emailed = True
            invoice.save()
        
        return HttpResponseRedirect('/invoices/')
        
class InvoiceFormView(View):
    template = 'invoice/invoice_form.html'
    
    def get(self,request,*args,**kwargs):
        invoice = Invoice.objects.get(id=kwargs['invoice_id']) if 'invoice_id' in kwargs else Invoice()
        trip = Trip.objects.get(id=kwargs['trip_id']) if 'trip_id' in kwargs else invoice.trip
        form = InvoiceForm(instance=invoice)
        formset = AdditionalCostFormSet(instance=invoice)
        return TemplateResponse(request,self.template,{
            'trip':trip,
            'form':form,
            'active':'invoice',
            'formset':formset,
            'companies':Company.objects.all(),
        })
        
    def post(self,request,*args,**kwargs):
        invoice = Invoice.objects.get(id=kwargs['invoice_id']) if 'invoice_id' in kwargs else None
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            invoice = form.save()
            
            invoice.trip.actual_miles = request.POST.get('actual_miles')
            invoice.trip.save()
            
            formset = AdditionalCostFormSet(request.POST,instance=invoice)
            if formset.is_valid():
                formset.save()
            else:
                return TemplateResponse(request,self.template,{'form':form})
        return HttpResponseRedirect('/invoices/')

class InvoiceDeleteView(View):
    
    def get(self,request,*args,**kwargs):
        """ This just deletes the invoice referenced by id """
        invoice = Invoice.objects.get(id=kwargs.get('id'))
        invoice.deleted = True
        invoice.save()
        
        return HttpResponseRedirect('/invoices/')

class InvoiceReactivateView(View):
    
    def get(self,request,*args,**kwargs):
        """ Reactive the invoice """
        invoice = Invoice.objects.get(id=kwargs.get('id'))
        invoice.deleted = False
        invoice.save()
        
        return HttpResponseRedirect('/invoice/view/{0}'.format(invoice.id))
    
class InvoiceView(View):
    template = 'invoice/invoice_view.html'
    
    def get(self,request,*args,**kwargs):
        return TemplateResponse(request,self.template,{
            'invoice':Invoice.objects.get(id=kwargs['id'])
        })

class InvoicePayView(View):
    template = 'invoice/invoice_pay.html'
    
    def get(self,request,*args,**kwargs):
        invoice = Invoice.objects.get(id=kwargs['id'])
        payment = Payment.objects.get(id=kwargs['payment_id']) if 'payment_id' in kwargs else None
        form = PaymentForm(instance=payment)
        return TemplateResponse(request,self.template,{
            'form':form,
            'payment':payment,
            'invoice':invoice,
        })
    
    def post(self,request,*args,**kwargs):
        invoice = Invoice.objects.get(id=kwargs['id'])
        payment = Payment.objects.get(id=kwargs['payment_id']) if 'payment_id' in kwargs else None
        form = PaymentForm(request.POST,instance=payment)
        if form.is_valid():
            payment = form.save()
        
        # check if it is completely paid, for query purposes
        if not invoice.owed:
            invoice.paid_off = True
            invoice.save()
        
        return HttpResponseRedirect('/invoice/{0}'.format(invoice.id))
        
class InvoicePrintView(View):
    template = 'invoice/invoice_print.html'
    
    def get(self,request,*args,**kwargs):
        invoice = Invoice.objects.get(id=kwargs['id'])
        return TemplateResponse(request,self.template,{'invoice':invoice})

class InvoiceSentView(View):
    
    def get(self,request,*args,**kwargs):
        invoice = Invoice.objects.get(id=kwargs.get('id'))
        invoice.faxed_emailed = True
        invoice.save()
        
        return HttpResponseRedirect('/invoice/view/{0}'.format(invoice.id))

class InvoiceStatusView(View):
    template = 'invoice_status.html'
    
    def get(self,request,*args,**kwargs):
        return TemplateResponse(request,self.template,{
            'invoice':Invoice.objects.get(id=kwargs['id'])
        })

class ProfileView(View):
    template = "profile_form.html"
    
    def get(self,request,*args,**kwargs):
        form = ProfileForm(instance=request.user.profile)
        return TemplateResponse(request,self.template,{'form':form})
    
    def post(self,request,*args,**kwargs):
        post_copy  = request.POST.copy()
        post_copy['user'] = request.user.id
        form = ProfileForm(post_copy,instance=request.user.profile)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect('/')

class ExitView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return HttpResponseRedirect('/')
