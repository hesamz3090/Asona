from django.urls import path
from .views import *


urlpatterns = [

    path('notification/', notification),
    path('verify/', verify),
    path('verify_code/', verify_code),
    path('sing_up/', sing_up),
    path('index/', index),
    path('category/', category),
    path('product/', product),
    path('distribution/', distribution),
    path('detail/', detail),
    path('cart/', cart),
    path('favorite/', favorite),
    path('state/', state),
    path('test/', test),
    path('show_all/', show_all),
    path('store/', store),
    path('payment/', payment),
    path('verify_payment/<panel>', verify_payment),
    path('add_order/', add_order),
    path('order/', order),

]
