from django.http import JsonResponse
import requests

BANK_URL = 'https://sc19jt.pythonanywhere.com'
# COMPANY_NAME = 'Card Payment Service'
class BankService:
    def getURL():
        return BANK_URL
    
    def exchangeCurrency(amount, currency):
        req = BANK_URL+f'/bank/exchange/{currency}/{amount}'
        print(req)
        try:
            response = requests.get(req)
            print("Converted amount: ", response.json().get('convertedAmount'))
            return response.json().get('convertedAmount')
        except:
            raise Exception('Unable to connect to bank service for currency exchange')
        
    def requestPayment(amount, recipientAccount, bookingId):
        req = BANK_URL+'/bank/pay'
        try:
            response = requests.post(req, json={
                'amount': amount,
                'companyName': recipientAccount,
                'bookingId': bookingId
            })
            print("Payment response: ", response.json())
            return response.json().get('status') == 'success'
        except:
            raise Exception('Unable to connect to bank service for payment')
        
    def requestRefund(bookingId):
        req = BANK_URL+'/bank/refund'
        try:
            response = requests.post(req, json={
                'bookingId': bookingId
            })
            print("Refund response: ", response.json())
            return response.json().get('status') == 'success'
        except:
            raise Exception('Unable to connect to bank service for refund')
        