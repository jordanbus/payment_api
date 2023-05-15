from debit_api.bank_service import BankService

def test_exchange_currency():
    amount = BankService.exchangeCurrency(100, 'USD')
    assert amount == 80