from django.db import models
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User,related_name='profile')

    company_name = models.CharField(blank=True, max_length=100)
    contact = models.CharField(blank=True, max_length=100)
    
    address = models.CharField(blank=True, max_length=100)
    city = models.CharField(blank=True, max_length=100)
    state = models.CharField(blank=True, max_length=100)
    zipcode = models.CharField(blank=True, max_length=100)
    
    mailing_address = models.CharField(blank=True, max_length=100)
    mailing_city = models.CharField(blank=True, max_length=100)
    mailing_state = models.CharField(blank=True, max_length=100)
    mailing_zipcode = models.CharField(blank=True, max_length=100)
    
    email = models.CharField(blank=True, max_length=100)
    phone_number = models.CharField(blank=True, max_length=100)
    fax_number = models.CharField(blank=True, max_length=100)
    
    def __unicode__(self):
        return self.company_name

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        exclude = []

class Company(models.Model):
    name = models.CharField(blank=True, max_length=100)
    contact = models.CharField(blank=True, max_length=100)
    email = models.CharField(blank=True, max_length=100)
    address = models.CharField(blank=True, max_length=100)
    city = models.CharField(blank=True, max_length=100)
    state = models.CharField(blank=True, max_length=100)
    zipcode = models.CharField(blank=True, max_length=100)
    mailing_address = models.CharField(blank=True, max_length=100)
    mailing_city = models.CharField(blank=True, max_length=100)
    mailing_state = models.CharField(blank=True, max_length=100)
    mailing_zipcode = models.CharField(blank=True, max_length=100)
    phone_number = models.CharField(blank=True, max_length=100)
    fax_number = models.CharField(blank=True, max_length=100)
    
    deleted = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural='Companies'
    
    def get_address(self):
        return "{0}, {1}, {2} {3}".format(
            self.address or "<none>",
            self.city or "<none>",
            self.state or "<none>",
            self.zipcode or "<none>"
        )
    
    def get_mailing_address(self):
        return "{0}, {1}, {2} {3}".format(
            self.mailing_address or "<none>",
            self.mailing_city or "<none>",
            self.mailing_state or "<none>",
            self.mailing_zipcode or "<none>"
        )
    
    def get_unpaid_invoices(self):
        """ this calls the invoices and whether they are paid """
        invoices = []
        for invoice in Invoice.objects.filter(trip__company=self):
            if invoice.owed:
                invoices.append(invoice)
        return invoices
    
    def get_all_invoices(self):
        """ this will return the all the invoices, paid or otherwise """
        return Invoice.objects.filter(trip__company=self)
    
    def get_unpaid_invoices_total(self):
        """ supplement for get_unpaid_invoices that sums the totals """
        return sum([invoice.price for invoice in self.get_unpaid_invoices()])
    
    def __unicode__(self):
        return self.name

class CompanyForm(ModelForm):
    class Meta:
        model = Company
        exclude = []

class Driver(models.Model):
    name = models.CharField(blank=True, max_length=100)
    dob = models.DateField(null=True,blank=True)
    phone_number = models.CharField(blank=True, max_length=100)
    
    address = models.CharField(blank=True, max_length=100)
    city = models.CharField(blank=True, max_length=100)
    state = models.CharField(blank=True, max_length=100)
    zipcode = models.CharField(blank=True, max_length=100)
    
    billing_address = models.CharField(blank=True, max_length=100)
    billing_city = models.CharField(blank=True, max_length=100)
    billing_state = models.CharField(blank=True, max_length=100)
    billing_zipcode = models.CharField(blank=True, max_length=100)
    
    deleted = models.BooleanField(default=False)
    
    def get_address(self):
        return "{0}, {1}, {2} {3}".format(
            self.address or "<none>",
            self.city or "<none>",
            self.state or "<none>",
            self.zipcode or "<none>"
        )
    
    def get_billing_address(self):
        return "{0}, {1}, {2} {3}".format(
            self.billing_address or "<none>",
            self.billing_city or "<none>",
            self.billing_state or "<none>",
            self.billing_zipcode or "<none>"
        )
    
    def __unicode__(self):
        return self.name

class DriverForm(ModelForm):
    class Meta:
        model = Driver
        exclude = []

class Trip(models.Model):
    """
    A trip will be a delivery.  It has a load and a company and other information
    """
    company = models.ForeignKey(Company)
    driver = models.ForeignKey(Driver)
    load_number = models.CharField(blank=True, max_length=100)
    rate = models.CharField(blank=True, max_length=100)
    miles = models.CharField(blank=True, max_length=100)
    actual_miles = models.CharField(blank=True, max_length=100)
    
    deleted = models.BooleanField(default=False)
    
    def get_from_information(self):
        """ from city state"""
        pickups = self.pickup_set.all()
        if pickups:
            pickup = pickups[0]
            if pickups.count() > 1:
                return '{0}, {1} [+]'.format(pickup.city.title(),pickup.state.upper())
            return '{0}, {1}'.format(pickup.city.title(),pickup.state.upper())
        return 'No information'
        
    def get_to_information(self):
        """ to city state """
        deliveries = self.delivery_set.all()
        if deliveries:
            delivery = deliveries[0]
            if deliveries.count() > 1:
                return '{0}, {1} [+]'.format(delivery.city.title(),delivery.state.upper())
            return '{0}, {1}'.format(delivery.city.title(),delivery.state.upper())
        return "No information"
    
    def get_pickup_date(self):
        """ return the first pickup's date """
        return self.pickup_set.all()[0].date if self.pickup_set.all() else 'No Date'
    
    def get_delivery_date(self):
        """ return the last delivery date """
        return self.delivery_set.latest('id').date if self.delivery_set.all() else 'No Date'
    
    def has_invoice(self):
        """ return if the trip has an invoice """
        return bool(self.invoice)
    
    def has_paid_invoice(self):
        """ return if the trip has paid invoice """
        return bool(self.invoice and self.invoice.payment_set.all())
    
    def __unicode__(self):
        return self.load_number

class TripForm(ModelForm):
    class Meta:
        model = Trip
        exclude = []

class Pickup(models.Model):
    """ this is a pickup attached to a trip, since it can have multiple pickups """
    STATES = (
        ("AL", "Alabama"),
        ("AK", "Alaska"),
        ("AS", "American Samoa"),
        ("AZ", "Arizona"),
        ("AR", "Arkansas"),
        ("CA", "California"),
        ("CO", "Colorado"),
        ("CT", "Connecticut"),
        ("DE", "Delaware"),
        ("DC", "District Of Columbia"),
        ("FM", "Federated States Of Micronesia"),
        ("FL", "Florida"),
        ("GA", "Georgia"),
        ("GU", "Guam"),
        ("HI", "Hawaii"),
        ("ID", "Idaho"),
        ("IL", "Illinois"),
        ("IN", "Indiana"),
        ("IA", "Iowa"),
        ("KS", "Kansas"),
        ("KY", "Kentucky"),
        ("LA", "Louisiana"),
        ("ME", "Maine"),
        ("MH", "Marshall Islands"),
        ("MD", "Maryland"),
        ("MA", "Massachusetts"),
        ("MI", "Michigan"),
        ("MN", "Minnesota"),
        ("MS", "Mississippi"),
        ("MO", "Missouri"),
        ("MT", "Montana"),
        ("NE", "Nebraska"),
        ("NV", "Nevada"),
        ("NH", "New Hampshire"),
        ("NJ", "New Jersey"),
        ("NM", "New Mexico"),
        ("NY", "New York"),
        ("NC", "North Carolina"),
        ("ND", "North Dakota"),
        ("MP", "Northern Mariana Islands"),
        ("OH", "Ohio"),
        ("OK", "Oklahoma"),
        ("OR", "Oregon"),
        ("PW", "Palau"),
        ("PA", "Pennsylvania"),
        ("PR", "Puerto Rico"),
        ("RI", "Rhode Island"),
        ("SC", "South Carolina"),
        ("SD", "South Dakota"),
        ("TN", "Tennessee"),
        ("TX", "Texas"),
        ("UT", "Utah"),
        ("VT", "Vermont"),
        ("VI", "Virgin Islands"),
        ("VA", "Virginia"),
        ("WA", "Washington"),
        ("WV", "West Virginia"),
        ("WI", "Wisconsin"),
        ("WY", "Wyoming"),
    )
    trip = models.ForeignKey(Trip)
    city = models.CharField(blank=True, max_length=100)
    state = models.CharField(blank=True, max_length=100, choices=STATES)
    zipcode = models.CharField(blank=True, max_length=100)
    date = models.DateField()
    
    def get_address_information(self):
        return '{0} {1}, {2}'.format(self.city,self.state, self.zipcode)
    
    def __unicode__(self):
        return self.city

PickupFormSet = inlineformset_factory(Trip,Pickup,extra=1,exclude=[])

class Delivery(models.Model):
    STATES = (
        ("AL", "Alabama"),
        ("AK", "Alaska"),
        ("AS", "American Samoa"),
        ("AZ", "Arizona"),
        ("AR", "Arkansas"),
        ("CA", "California"),
        ("CO", "Colorado"),
        ("CT", "Connecticut"),
        ("DE", "Delaware"),
        ("DC", "District Of Columbia"),
        ("FM", "Federated States Of Micronesia"),
        ("FL", "Florida"),
        ("GA", "Georgia"),
        ("GU", "Guam"),
        ("HI", "Hawaii"),
        ("ID", "Idaho"),
        ("IL", "Illinois"),
        ("IN", "Indiana"),
        ("IA", "Iowa"),
        ("KS", "Kansas"),
        ("KY", "Kentucky"),
        ("LA", "Louisiana"),
        ("ME", "Maine"),
        ("MH", "Marshall Islands"),
        ("MD", "Maryland"),
        ("MA", "Massachusetts"),
        ("MI", "Michigan"),
        ("MN", "Minnesota"),
        ("MS", "Mississippi"),
        ("MO", "Missouri"),
        ("MT", "Montana"),
        ("NE", "Nebraska"),
        ("NV", "Nevada"),
        ("NH", "New Hampshire"),
        ("NJ", "New Jersey"),
        ("NM", "New Mexico"),
        ("NY", "New York"),
        ("NC", "North Carolina"),
        ("ND", "North Dakota"),
        ("MP", "Northern Mariana Islands"),
        ("OH", "Ohio"),
        ("OK", "Oklahoma"),
        ("OR", "Oregon"),
        ("PW", "Palau"),
        ("PA", "Pennsylvania"),
        ("PR", "Puerto Rico"),
        ("RI", "Rhode Island"),
        ("SC", "South Carolina"),
        ("SD", "South Dakota"),
        ("TN", "Tennessee"),
        ("TX", "Texas"),
        ("UT", "Utah"),
        ("VT", "Vermont"),
        ("VI", "Virgin Islands"),
        ("VA", "Virginia"),
        ("WA", "Washington"),
        ("WV", "West Virginia"),
        ("WI", "Wisconsin"),
        ("WY", "Wyoming"),
    )
    trip = models.ForeignKey(Trip)
    city = models.CharField(blank=True, max_length=100)
    state = models.CharField(blank=True, max_length=100, choices=STATES)
    zipcode = models.CharField(blank=True, max_length=100)
    date = models.DateField()
    
    def get_address_information(self):
        return '{0} {1}, {2}'.format(self.city,self.state, self.zipcode)
    
    def __unicode__(self):
        return self.city

DeliveryFormSet = inlineformset_factory(Trip,Delivery,extra=1,exclude=[])
    
class Invoice(models.Model):
    number = models.CharField(blank=True, max_length=100)
    trip = models.OneToOneField(Trip)
    date_entered = models.DateField(auto_now_add=True)
    date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    faxed_emailed = models.BooleanField(default=False)
    paidoff = models.BooleanField(default=False)
    
    deleted = models.BooleanField(default=False)
    
    def paid(self):
        """ shortcut to tell if this invoice has been paid """
        return bool(self.payment_set.all())
    
    def owed(self):
        """ calculate how much is owed """
        return self.get_total() - self.get_payment_total()
    
    def get_payment_total(self):
        """ how much has been paid """
        return sum([payment.amount for payment in self.payment_set.all()])
    
    def get_total(self):
        """ this function will add the price, plus any additional costs """
        return self.price + sum([additional_cost.cost for additional_cost in self.additionalcost_set.all()])
    
    def __unicode__(self):
        return self.number

class InvoiceForm(ModelForm):
    class Meta:
        model = Invoice
        exclude = []

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice)
    date_entered = models.DateField(auto_now_add=True)
    date_of_payment = models.DateField()
    check_number = models.CharField(blank=True, max_length=100)
    direct_deposit_number = models.CharField(blank=True, max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def get_check_or_direct_deposit_info(self):
        if self.check_number:
            return "Check Number {0}".format(self.check_number)
        return "Direct Deposit Number {0}".format(self.direct_deposit_number)
    
    def __unicode__(self):
        return "Payment for Invoice {0}".format(self.invoice)

class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        exclude = []

class AdditionalCost(models.Model):
    invoice = models.ForeignKey(Invoice)
    name = models.CharField(blank=True, max_length=100)
    description = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __unicode__(self):
        return self.name

class AdditionalCostForm(ModelForm):    
    class Meta:
        model = AdditionalCost
        exclude = []

AdditionalCostFormSet = inlineformset_factory(Invoice,AdditionalCost,extra=0,exclude=[])