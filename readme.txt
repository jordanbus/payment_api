# README

i. The name of your pythonanywhere domain.

http://sc20jwb.pythonanywhere.com/

/payments/refund

ii. The password I have to use to login to my admin account on your service.

P@ss1234

iii. Any other information I need in order to use your service.

endpoints available:

/payments/form

/payments/pay

/payments/refund

When adding a card from admin page, expiry date includes a day, however this will be overwritten to be the first day of the month when saved, since expiry dates are only month year. 

Card numbers are hashed, hence when saved viewing them again will not be possible. They also shouldn’t be changed after creating, since they are only hashed the first time they are saved.

Available card to use:

"cardNumber": "4619648111834096",
"cvv": "140",
"expiryDate": "05/33",
"name": "Sharon Castaneda",
"email": "[scastaneda@email.com](mailto:scastaneda@email.com)"
