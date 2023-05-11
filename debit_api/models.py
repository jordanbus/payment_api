from django.db import models

# Create your models here.
class Card(models.Model):
    cardId = models.IntegerField(primary_key=True)
    cardNumber = models.CharField(max_length = 16)
    cardType = models.CharField(max_length = 20)
    cvv = models.CharField(max_length = 3)
    salt = models.CharField(max_length = 30)
    expiryDate = models.DateField()
    name = models.CharField(max_length = 180)
    balance = models.FloatField()
    accountCurrencyId = models.IntegerField()
    
class Transaction(models.Model):
    transactionId = models.IntegerField(primary_key=True)
    cardId = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='transactionCardId')
    transactionDate = models.DateTimeField()
    transactionAmount = models.FloatField()
    transactionCurrencyId = models.IntegerField()
    transactionFee = models.FloatField()
    confirmed = models.BooleanField()
    recipientCardId = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='transactionRecipientCardId')
    
    def __str__(self):
        return self.transactionId
    
class Billing(models.Model):
    cardId = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='billingCardId')
    firstName = models.CharField(max_length = 180)
    lastName = models.CharField(max_length = 180)
    addressLine1 = models.CharField(max_length = 180)
    addressLine2 = models.CharField(max_length = 180, blank=True, null=True)
    postCode = models.CharField(max_length = 8)
    country = models.CharField(max_length = 56)
    phoneNumber = models.CharField(max_length = 20)
    
    def __str__(self):
        return self.billingId