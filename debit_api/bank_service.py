from django.http import JsonResponse
import requests

BANK_URLS = [
    'https://sc19jt.pythonanywhere.com',
    'https://sc20wrpf.pythonanywhere.com/'
]

# COMPANY_NAME = 'Card Payment Service'
class BankService:
    
    def exchangeCurrency(amount, currency):
        for BANK_URL in BANK_URLS:
            req = BANK_URL+f'/bank/exchange/{currency}/{amount}'
            print('Trying to connect to: ', req)
            try:
                response = requests.get(req)
                print("Converted amount: ", response.json().get('convertedAmount'))
                return response.json().get('convertedAmount')
            except:
                print('Unable to connect to bank service for currency exchange')
                # raise Exception('Unable to connect to bank service for currency exchange')
        return -1
        
    def requestPayment(amount, recipientAccount, bookingId):
        success = False
        for BANK_URL in BANK_URLS:
            if not success:
                req = BANK_URL+'/bank/pay'
                print('Trying to connect to: ', req)
                try:
                    payload = {
                        'amount': amount,
                        'companyName': recipientAccount,
                        'bookingID': bookingId
                    } 
                    print("Payment request: ", payload)
                    response = requests.post(req, json=payload)
                    print("Payment response: ", response.json())
                    success = response.json().get('status') == 'success'
                except:
                    # raise Exception('Unable to connect to bank service for payment')
                    print('Unable to connect to bank service for payment')
        return success
        
    def requestRefund(bookingId):
        success = False
        for BANK_URL in BANK_URLS:
            if not success:
                req = BANK_URL+'/bank/refund'
                print('Trying to connect to: ', req)

                try:
                    payload = {
                        'bookingID': bookingId
                    }
                    print("Refund request: ", payload)
                    response = requests.post(req, json=payload)
                    print("Refund response: ", response.json())
                    success = response.json().get('status') == 'success'
                except:
                    # raise Exception('Unable to connect to bank service for refund')
                    print('Unable to connect to bank service for refund')
        return success
        