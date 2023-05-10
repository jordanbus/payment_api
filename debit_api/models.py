from django.db import models

# Create your models here.
class User(models.Model):
    userId = models.IntegerField(primary_key=True)
    username = models.CharField(max_length = 180)
    email = models.CharField(max_length = 180)
    password = models.CharField(max_length = 180)
    salt = models.CharField(max_length = 8)
    balance = models.FloatField()
    accountCurrencyId = models.IntegerField()
    
    def __str__(self):
        return self.userId
    
class PendingTransaction(models.Model):
    transactionId = models.IntegerField(primary_key=True)
    userId = models.IntegerField()
    transactionAmount = models.FloatField()
    transactionDueDate = models.DateTimeField()
    transactionCurrencyId = models.IntegerField()
    transactionFee = models.FloatField()
    installmentNumber = models.IntegerField()
    
    def __str__(self):
        return self.transactionId
    
class Transaction(models.Model):
    transactionId = models.IntegerField(primary_key=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactionUserId')
    transactionDate = models.DateTimeField()
    transactionAmount = models.FloatField()
    transactionCurrencyId = models.IntegerField()
    transactionFee = models.FloatField()
    confirmed = models.BooleanField()
    recipientAccountId = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactionRecipientAccountId')
    # installmentNumber = models.IntegerField()
    
    def __str__(self):
        return self.transactionId
    
class Billing(models.Model):
    # userId = models.IntegerField(primary_key=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE, related_name='billingUserId')
    firstName = models.CharField(max_length = 180)
    lastName = models.CharField(max_length = 180)
    addressLine1 = models.CharField(max_length = 180)
    addressLine2 = models.CharField(max_length = 180)
    postCode = models.CharField(max_length = 20)
    country = models.CharField(max_length = 100)
    phoneNumber = models.CharField(max_length = 20)
    
    def __str__(self):
        return self.billingId