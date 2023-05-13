import pytest
import requests
import datetime
import random

HOST = 'http://127.0.0.1:8000/'


testCards = [
    {
        "cardNumber": "4619648111834096287",
        "cvv": "140",
        "expiryDate": datetime.datetime.strptime("2033-05-13", "%Y-%m-%d"),
        "cardType": "Debit",
        "name": "Sharon Castaneda",
        "email": "scastaneda@email.com"
    },
    {
        "cardNumber": "4235151774575",
        "cvv": "423",
        "expiryDate": datetime.datetime.strptime("2024-05-13", "%Y-%m-%d"),
        "cardType": "Debit",
        "name": "Michael Ramsey",
        "email": "michael.ramsey@email.com"
    },
    {
        "cardNumber": "639028529274",
        "cvv": "454",
        "expiryDate": datetime.datetime.strptime("2028-06-10", "%Y-%m-%d"),
        "cardType": "Debit",
        "name": "Sarah Johnson",
        "email": "johnsonsarah@email.com"
    }
]

airlines = [
    "ed19km2b",
     "mavericklow"
     "krzsztfkml"
     "safwanchowdhury"
]


def test_form_endpoint():
    response = requests.get(HOST+'payments/form')
    assert response.status_code == 200
    assert response.json() == {'fields': {
        'cardNumber': 'string',
        'cvv': 'string',
        'expiryDate': 'date',
        'name': 'string',
        'email': 'string'
    }}
    
def test_pay_endpoint():
    card = testCards[random.randint(0, len(testCards)-1)]
    response = requests.post(HOST+'payments/pay', json={
        'form': {
            'cardNumber': card['cardNumber'],
            'cvv': card['cvv'], 
            'expiryDate': card['expiryDate'].strftime("%Y-%m-%d"), 
            'name': card['name'], 
            'email': card['email'],
        },
        'transaction': {
            'transactionAmount': random.randint(1, 1000),
            'currency': 'EUR',
            'recipientAccount': airlines[random.randint(0, len(airlines)-1)],
            'bookingId': -1,
        }
    })
    
    assert response.status_code == 200
    assert response.json() == {'status': 'success', 'transactionID': None}
    
def test_refund_endpoint():
    card = testCards[random.randint(0, len(testCards)-1)]
    
    response = requests.post(HOST+'payments/refund', json={
        'transactionID': 1,
        'bookingId': -1,
        'form': {
            'cardNumber': card['cardNumber'],
            'cvv': card['cvv'], 
            'expiryDate': card['expiryDate'].strftime("%Y-%m-%d"), 
            'name': card['name'], 
            'email': card['email'],
        },
    })
    assert response.status_code == 200
    assert response.json() == {'status': 'failed', 'error': 'Transaction not found'}