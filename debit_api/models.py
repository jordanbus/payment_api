from django.db import models
from enum import Enum
import bcrypt

# Create your models here.
class Currency(models.Model):
    currencyId = models.AutoField(primary_key=True)
    currencyName = models.CharField(max_length = 50)
    currencyCode = models.CharField(max_length = 3)

class Card(models.Model):
    cardId = models.AutoField(primary_key=True)
    cardNumber = models.CharField(max_length = 60)
    cardType = models.CharField(max_length = 20)
    cvv = models.CharField(max_length = 3)
    salt = models.CharField(max_length = 60)
    expiryDate = models.DateField()
    name = models.CharField(max_length = 180)
    balance = models.FloatField()
    accountCurrency = models.ForeignKey('Currency', on_delete=models.DO_NOTHING, related_name='cardAccountCurrency')
    email = models.CharField(max_length = 180)
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only generate salt and hash on initial save
            salt = bcrypt.gensalt()
            hashedCardNumber = bcrypt.hashpw(self.cardNumber.encode(), salt)
            self.cardNumber = hashedCardNumber.decode()
            self.salt = salt.decode()
        
        # Set expiry date to first day of the month for all cards
        self.expiryDate = self.expiryDate.replace(day=1)
        super().save(*args, **kwargs)
    
class TransactionStatus(Enum):
    CONFIRMED = 1
    PENDING = 2
    DECLINED = 3
    REFUNDED = 4
    REFUND_PENDING = 5

class Transaction(models.Model):
    transactionId = models.AutoField(primary_key=True)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='transactionCard')
    transactionDate = models.DateTimeField(auto_now_add=True)
    transactionAmount = models.FloatField()
    transactionCurrency = models.ForeignKey('Currency', on_delete=models.DO_NOTHING, related_name='transactionCurrency')
    transactionFee = models.FloatField()
    status = models.IntegerField()
    recipient = models.CharField(max_length = 180)
    # recipientCard = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='transactionRecipientCard')

class Billing(models.Model):
    card = models.ForeignKey(Card, on_delete=models.DO_NOTHING, related_name='billingCard')
    firstName = models.CharField(max_length = 180)
    lastName = models.CharField(max_length = 180)
    addressLine1 = models.CharField(max_length = 180)
    addressLine2 = models.CharField(max_length = 180, blank=True, null=True)
    postCode = models.CharField(max_length = 8)
    country = models.CharField(max_length = 56)
    phoneNumber = models.CharField(max_length = 20)
