from django.contrib import admin
from .models import User, Billing, Transaction, PendingTransaction

# Register your models here.
admin.site.register(User)
admin.site.register(Billing)
admin.site.register(Transaction)
admin.site.register(PendingTransaction)