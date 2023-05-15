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

#  Hash the card number using the salt
def hashCardNumber(cardNumber, salt):
    hashedCardNumber = bcrypt.hashpw(cardNumber.encode(), salt.encode())
    return hashedCardNumber.decode()

#  Search for a card using specified parameters
def getCardIdIfExists(cardNumber, cvv, expiryDate, name, email):
    cardId = -1
    if cardNumber and cvv and expiryDate and name and email:
        cards = Card.objects.filter(cvv=cvv, expiryDate=expiryDate, name=name, email=email)
        for card in cards:
            # Make sure the card exists and the card number matches the hashed card number in the db
            if card and card.cardNumber == hashCardNumber(cardNumber, card.salt):
                cardId = card.cardId
    
    return cardId

#  Convert the amount to GBP if necessary
def convertCurrencyToGBP(amount, currency):
    if currency != 'GBP':
        try:
            amount = BankService.exchangeCurrency(amount, currency)
            if amount is None:
                return -1
        except:
            print('Error converting currency')
            return -1
    return amount

#  Check if the card exists and has sufficient balance
def checkCardBalance(cardId, amount):
    card = Card.objects.filter(cardId=cardId).first()
    if card:
        if card.balance >= amount:
            return True
    return False

# Create a pending transaction object for the booking
def createTransaction(cardId, recipientName, amount):
    transactionId = -1
    
    # Retrieve the card object
    card = Card.objects.select_for_update().get(cardId=cardId)
    # Create the transaction object
    newTransaction = Transaction(
        card=card,
        recipient=recipientName,
        transactionAmount=amount,
        transactionCurrency=card.accountCurrency,
        transactionFee=0,
        # Status is pending since not confirmed by bank yet
        status=TransactionStatus.PENDING.value
    )
    newTransaction.save()
    transactionId = newTransaction.transactionId
    return transactionId

#  Confirm transaction and deduct funds from card balance
def confirmTransaction(transactionId):
    try:
        with transaction.atomic():
            # Retrieve the transaction object
            userTransaction = Transaction.objects.select_for_update().get(transactionId=transactionId)
            
            # Retrieve the card object
            card = userTransaction.card
            
             # Remove the amount from the card balance
            card.balance -= userTransaction.transactionAmount
            card.save()
            
            # Set the transaction status to confirmed
            userTransaction.status = TransactionStatus.CONFIRMED.value
            userTransaction.save()

        # Commit the transaction
        transaction.commit()
        return True

    except Exception as e:
        # Rollback the transaction, since an error occurred
        transaction.rollback()
        return False
    
# Refund transaction and return funds to card balance
def refundTransaction(transactionId):
    try:
        with transaction.atomic():
            # Retrieve the transaction object
            userTransaction = Transaction.objects.select_for_update().get(transactionId=transactionId)
            
            # Retrieve the card object
            card = userTransaction.card
            
             # Return the amount to the card balance
            card.balance += userTransaction.transactionAmount
            card.save()
            
            # Set the transaction status to refunded
            userTransaction.status = TransactionStatus.REFUNDED.value
            userTransaction.save()

            # Commit the transaction
        transaction.commit()
        return True
    except Exception as e:
        # Rollback the transaction, since an error occurred
        transaction.rollback()
        return False
    

# Return form fields to use for card payment
@require_http_methods(['GET'])
def form(request):
    return JsonResponse({'fields': {'cardNumber': 'Enter your card number: ',
                                    'cvv': 'Enter your CVV: ', 
                                    'expiryDate': 'Enter your expiry date (MM/YY): ', 
                                    'name': 'Enter your full name: ', 
                                    'email': 'Enter your email address: '}})

# Make a payment for a booking
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
        amount = transaction.get('amount')
        currency = transaction.get('currency')
        recipientAccount = transaction.get('recipientAccount')
        bookingId = transaction.get('bookingID')
        
        expiryDate = datetime.datetime.strptime(expiryDate, '%m/%y').date()
    except:
        return JsonResponse({'status': 'failed', 'error': 'Invalid . Could not parse JSON'})
    
    if fields is None or cardNumber is None or cvv is None or expiryDate is None or name is None or email is None or transaction is None or amount is None or currency is None or recipientAccount is None or bookingId is None:
        return JsonResponse({'status': 'failed', 'error': 'Invalid request. Missing fields'})
    
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
        if currency != Card.objects.get(cardId=cardId).accountCurrency.currencyCode:
            return JsonResponse({'status': 'failed', 'error': 'Currency mismatch with account. Please use the currency used for the account.',  'transactionId': -1})
    else:
        # If user's account is in GBP, then allow other currencies since they will be converted to GBP
        amount = amountInGBP
    
    # Check card balance
    if not checkCardBalance(cardId, amount):
        return JsonResponse({'status': 'failed', 'error': 'Insufficient funds', 'transactionId': -1})
    
    
    # Start a pending transaction
    transactionId = createTransaction(cardId, recipientAccount, amount)
    if transactionId == -1:
        return JsonResponse({'status': 'failed', 'error': 'Transaction could not be made. Please try again.', 'transactionId': transactionId})
    
    # Send request to bank
    accepted = BankService.requestPayment(amountInGBP, recipientAccount, bookingId)
    if not accepted:
        # Remove pending transaction since no confirmation from bank
        Transaction.objects.filter(transactionId=transactionId).delete()
        return JsonResponse({'status': 'failed', 'error': 'Bank rejected payment', 'transactionId': transactionId})
    
    # Confirm transaction and deduct funds after confirmation from bank
    confirmed = confirmTransaction(transactionId)
    if not confirmed:
        return JsonResponse({'status': 'failed', 'error': 'Transaction could not be confirmed. Please try again.',  'transactionId': transactionId})
    
    # Return status and transaction ID
    return JsonResponse({'status': 'success', 'TransactionID': transactionId})
    

@csrf_exempt
@require_http_methods(['POST'])
def refund(request):

    try:
        data = json.loads(request.body)
        transactionId = data.get('TransactionID')
        bookingId = data.get('BookingID')
        fields = data.get('fields')
        cardNumber = fields.get('cardNumber')
        cvv = fields.get('cvv')
        expiryDate = fields.get('expiryDate')
        name = fields.get('name')
        
        expiryDate = datetime.datetime.strptime(expiryDate, '%m/%y').date()
    except:
        return JsonResponse({'status': 'failed', 'error': 'Invalid . Could not parse JSON'})
    
    if transactionId is None or bookingId is None or fields is None or cardNumber is None or cvv is None or expiryDate is None or name is None:
        return JsonResponse({'status': 'failed', 'error': 'Invalid request. Missing fields'})
    
    # Check if transaction exists for card details
    transactions = Transaction.objects.filter(transactionId=transactionId, card__cvv=cvv, card__expiryDate=expiryDate, card__name=name)
    transactionId = -1
    for transaction in transactions:
        if transaction.status == TransactionStatus.CONFIRMED.value and transaction.card.cardNumber == hashCardNumber(cardNumber, transaction.card.salt):
            transactionId = transaction.transactionId
            break
    
    if transactionId == -1:
        return JsonResponse({'status': 'failed', 'error': 'Transaction not found'})

    # Change transaction status
    transaction = Transaction.objects.select_for_update().get(transactionId=transactionId)
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
