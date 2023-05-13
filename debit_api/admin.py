from django.contrib import admin
from .models import Card, Billing, Transaction, Currency

# Register your models here.
admin.site.register(Card)
admin.site.register(Billing)
admin.site.register(Transaction)
admin.site.register(Currency)