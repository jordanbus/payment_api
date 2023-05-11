import pytest
import requests

HOST = 'http://127.0.0.1:8000/'

def test_form_endpoint():
    response = requests.get(HOST+'payments/form')
    assert response.status_code == 200
    assert response.json() == {'fields': {
        'cardNumber': 'string',
        'cvv': 'string', 
        'expiryDate': 'date', 
        'name': 'string', 
        'email': 'string'}}
    
def test_pay_endpoint():
    response = requests.post(HOST+'payments/pay', json={
        'form': {
            'cardNumber': 'string',
            'cvv': 'string', 
            'expiryDate': 'date', 
            'name': 'string', 
            'email': 'string'
        },
        'transaction': {
            'transactionAmount': 'string',
            'currency': 'string',
            'recipientAccount': 'string',
            'reference': 'string'
        }
    })
    
    assert response.status_code == 200
    assert response.json() == {'status': 'success', 'transactionID': None}
    
def test_refund_endpoint():
    response = requests.post(HOST+'payments/refund', json={
        'transactionID': 1,
        'form': {
            'cardNumber': 'string',
            'cvv': 'string', 
            'expiryDate': 'date', 
            'name': 'string', 
        },
    })
    assert response.status_code == 200
    assert response.json() == {'status': 'success', 'transactionId': 1}