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
    currency = data.get('currency')
    reservationId = data.get('reservationId')

    transaction_id = None
   
    return JsonResponse({'status': 'success', 'TransactionID': transaction_id})


@csrf_exempt
@require_http_methods(['POST'])
def refund(request):

    data = json.loads(request.body)
    transaction_id = data.get('transactionID')
    form = data.get('form')
    cardNumber = form.get('cardNumber')
    cvv = form.get('cvv')
    expiryDate = form.get('expiryDate')
    name = form.get('name')
    email = form.get('email')
    currency = data.get('currency')
    reservationId = data.get('reservationId')

    try:
        pass
    except:
        return JsonResponse({'status': 'failed', 'error': 'Transaction does not exist'})
    return JsonResponse({'status': 'success', 'transactionId': transaction_id})
