from django.contrib import admin
from .models import Card, Billing, Transaction, Currency
from django import forms
class CardForm(forms.ModelForm):
    cardType = forms.ChoiceField(
        choices=[('Visa', 'Visa'), ('MasterCard', 'MasterCard')],
        widget=forms.RadioSelect
    )
    
    class Meta:
        model = Card
        fields = '__all__'

class CardAdmin(admin.ModelAdmin):
    form = CardForm
    list_display = (
        'cardNumber',
        'cardType',
        'cvv',
        'expiryDate', 
        'name', 
        'balance',
        'accountCurrency',
        'email',
    )
    # Specify other customization options as needed
    def get_exclude(self, request, obj=None):
        exclude = super().get_exclude(request, obj)
        if exclude is None:
            exclude = []
        exclude.append('salt')
        return exclude
    
# Register the Card model with the custom admin class
admin.site.register(Card, CardAdmin)
admin.site.register(Billing)
admin.site.register(Transaction)
admin.site.register(Currency)