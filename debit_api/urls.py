from django.urls import path
from . import views

urlpatterns = [
    path('form', views.form),
    path('pay', views.pay),
    path('refund', views.refund),
]