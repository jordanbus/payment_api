from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Card, Billing, Transaction, TransactionStatus
import json
from .bank_service import BankService
from django.db import transaction
import datetime
import bcrypt

# Create your views here.


def hashCardNumber(cardNumber, salt):
    hashedCardNumber = bcrypt.hashpw(cardNumber.encode(), salt.encode())
    return hashedCardNumber.decode()

def getCardIdIfExists(cardNumber, cvv, expiryDate, name, email):
    cardId = -1
    if cardNumber and cvv and expiryDate and name and email:
        card = Card.objects.filter(cvv=cvv, expiryDate=expiryDate, name=name, email=email).first()
        if card and card.cardNumber == hashCardNumber(cardNumber, card.salt):
            cardId = card.cardId
    
    return cardId

def convertCurrencyToGBP(amount, currency):
    amount = -1
    if currency != 'GBP':
        try:
            amount = BankService.exchangeCurrency(amount, currency)
            if amount is None:
                amount = -1
        except:
            print('Error converting currency')
    return amount

def checkCardBalance(cardId, amount):
    card = Card.objects.filter(cardId=cardId).first()
    if card:
        if card.balance >= amount:
            return True
    return False
    
def createTransaction(cardId, recipientName, amount):
    transactionId = -1
    try:
        with transaction.atomic():
            # Retrieve the card objects
            card = Card.objects.select_for_update().get(cardId=cardId)

            # Create the transaction object
            newTransaction = Transaction(
                card=card,
                recipient=recipientName,
                transactionAmount=amount,
                transactionCurrencyId=1,
                transactionFee=0,
                status=TransactionStatus.PENDING.value
            )
            newTransaction.save()

        # Commit the transaction
        transaction.commit()
        transactionId = newTransaction.transactionId

    except Exception as e:
        print(e)
        # Handle the exception or rollback the transaction if needed
        transaction.rollback()

    return transactionId

def confirmTransaction(transactionId):
    try:
        with transaction.atomic():
            # Retrieve the transaction objects
            userTransaction = Transaction.objects.select_for_update().get(transactionId=transactionId)
            
            # Retrieve the card objects
            card = userTransaction.card
            
             # Perform necessary operations
            card.balance -= userTransaction.transactionAmount
            card.save()
            
            # Perform necessary operations
            userTransaction.status = TransactionStatus.CONFIRMED.value
            userTransaction.save()

        # Commit the transaction
        transaction.commit()
        return True

    except Exception as e:
        # Handle the exception or rollback the transaction if needed
        transaction.rollback()
        return False
    
def refundTransaction(transactionId):
    try:
        with transaction.atomic():
            # Retrieve the transaction objects
            userTransaction = Transaction.objects.select_for_update().get(transactionId=transactionId)
            
            # Retrieve the card objects
            card = userTransaction.card
            
             # Perform necessary operations
            card.balance += userTransaction.transactionAmount
            card.save()
            
            # Perform necessary operations
            userTransaction.status = TransactionStatus.REFUNDED.value
            userTransaction.save()

            # Commit the transaction
        transaction.commit()
        return True
    except Exception as e:
        # Handle the exception or rollback the transaction if needed
        transaction.rollback()
        return False
    

@require_http_methods(['GET'])
def form(request):
    return JsonResponse({'fields': {'cardNumber': 'Enter your card number: ',
                                    'cvv': 'Enter your CVV: ', 
                                    'expiryDate': 'Enter your expiry date (MM/YY): ', 
                                    'name': 'Enter your full name: ', 
                                    'email': 'Enter your email address: '}})

@csrf_exempt
@require_http_methods(['POST'])
def pay(request):
    try:
        # Get data from request
        data = json.loads(request.body)
        fields = data.get('fields')
        cardNumber = fields.get('cardNumber')
        cvv = fields.get('cvv')
        expiryDate = fields.get('expiryDate')
        name = fields.get('name')
        email = fields.get('email')
        transaction = data.get('transaction')
        amount = transaction.get('transactionAmount')
        currency = transaction.get('currency')
        recipientAccount = transaction.get('recipientAccount')
        bookingId = transaction.get('bookingId')
        
        expiryDate = datetime.datetime.strptime(expiryDate, '%m/%y').date()
    except:
        return JsonResponse({'status': 'failed', 'error': 'Invalid . Could not parse JSON'})
    
    
    # Check if card exists
    cardId = getCardIdIfExists(cardNumber, cvv, expiryDate, name, email)
    
    if cardId == -1:
        return JsonResponse({'status': 'failed', 'error': 'Card not found'})
    
   
       
    # Convert currency to GBP for bank payment
    amountInGBP = convertCurrencyToGBP(amount, currency)
    if amountInGBP == -1:
        return JsonResponse({'status': 'failed', 'error': f'Currency conversion not available for {currency}', 'transactionId': -1})
    
    # Make sure currency matches account currency or can be converted to account currency (ONLY GBP supported for now)
    accountCurrency = Card.objects.get(cardId=cardId).accountCurrency.currencyCode
    if accountCurrency != 'GBP':
        if currency != Card.objects.get(cardId=cardId).accountCurrency:
            return JsonResponse({'status': 'failed', 'error': 'Currency mismatch with account. Please use the currency used for the account.',  'transactionId': -1})
    else:
        amount = amountInGBP
    
    # Check card balance
    if not checkCardBalance(cardId, amount):
        return JsonResponse({'status': 'failed', 'error': 'Insufficient funds', 'transactionId': -1})
    
    
    # Start transaction
    transactionId = createTransaction(cardId, recipientAccount, amount)
    if transactionId == -1:
        return JsonResponse({'status': 'failed', 'error': 'Transaction could not be made. Please try again.', 'transactionId': transactionId})
    
    # Send request to bank
    accepted = BankService.requestPayment(amountInGBP, recipientAccount, bookingId)
    if not accepted:
        # Remove pending transaction
        Transaction.objects.filter(transactionId=transactionId).delete()
        return JsonResponse({'status': 'failed', 'error': 'Bank rejected payment', 'transactionId': transactionId})
    
    # Confirm transaction
    confirmed = confirmTransaction(transactionId)
    if not confirmed:
        return JsonResponse({'status': 'failed', 'error': 'Transaction could not be confirmed. Please try again.',  'transactionId': transactionId})
    
    # Return status and transaction ID
    return JsonResponse({'status': 'success', 'transactionID': transactionId})
    

@csrf_exempt
@require_http_methods(['POST'])
def refund(request):

    try:
        data = json.loads(request.body)
        transactionId = data.get('transactionID')
        bookingId = data.get('bookingID')
        fields = data.get('fields')
        cardNumber = fields.get('cardNumber')
        cvv = fields.get('cvv')
        expiryDate = fields.get('expiryDate')
        name = fields.get('name')
        
        expiryDate = datetime.datetime.strptime(expiryDate, '%m/%y').date()
    except:
        return JsonResponse({'status': 'failed', 'error': 'Invalid . Could not parse JSON'})
    
    # Check if transaction exists for card details
    transaction = Transaction.objects.filter(transactionId=transactionId, card__cvv=cvv, card__expiryDate=expiryDate, card__name=name).first()
    if not(transaction and 
           transaction.status == TransactionStatus.CONFIRMED.value and 
           transaction.card.cardNumber == hashCardNumber(cardNumber, transaction.card.salt)):
        return JsonResponse({'status': 'failed', 'error': 'Transaction not found'})

    # Change transaction status
    transaction = Transaction.objects.select_for_update().get(transactionId=transaction.transactionId)
    transaction.status = TransactionStatus.REFUND_PENDING.value
    transaction.save()

    success = BankService.requestRefund(bookingId)

    if not success:
        # Revert refund status to confirmed if not refunded
        transaction.status = TransactionStatus.CONFIRMED.value
        transaction.save()
        return JsonResponse({'status': 'failed', 'error': 'Bank rejected refund'})
    
    success = refundTransaction(transactionId)
    if not success:
        return JsonResponse({'status': 'failed', 'error': 'Transaction could not be refunded. Please try again.'})
    
    return JsonResponse({'status': 'success'})
