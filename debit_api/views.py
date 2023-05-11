from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Card, Billing, Transaction
import json

# Create your views here.


@require_http_methods(['GET'])
def form(request):
    return JsonResponse({'fields': {'cardNumber': 'string',
                                    'cvv': 'string', 
                                    'expiryDate': 'date', 
                                    'name': 'string', 
                                    'email': 'string'}})


@csrf_exempt
@require_http_methods(['POST'])
def pay(request):
    data = json.loads(request.body)
    form = data.get('form')
    cardNumber = form.get('cardNumber')
    cvv = form.get('cvv')
    expiryDate = form.get('expiryDate')
    name = form.get('name')
    email = form.get('email')
    transaction = data.get('transaction')
    amount = transaction.get('transactionAmount')
    currency = transaction.get('currency')
    recipientAccount = transaction.get('recipientAccount')
    reference = transaction.get('reference')
    
    # card = Card.objects.filter(cardNumber=cardNumber, cvv=cvv, expiryDate=expiryDate, name=name, email=email)
    # if not card:
    #     card = Card(cardNumber=cardNumber, cvv=cvv, expiryDate=expiryDate, name=name, email=email)
    #     card.save()
        
    # transaction = Transaction(card=card, amount=amount, currency=currency, recipientAccount=recipientAccount, reference=reference)
    # transaction = transaction.save()
    return JsonResponse({'status': 'success', 'transactionID': None})


@csrf_exempt
@require_http_methods(['POST'])
def refund(request):

    data = json.loads(request.body)
    transactionId = data.get('transactionID')
    form = data.get('form')
    cardNumber = form.get('cardNumber')
    cvv = form.get('cvv')
    expiryDate = form.get('expiryDate')
    name = form.get('name')

    try:
        pass
    except:
        return JsonResponse({'status': 'failed', 'error': 'Transaction does not exist'})
    return JsonResponse({'status': 'success', 'transactionId': transactionId})
