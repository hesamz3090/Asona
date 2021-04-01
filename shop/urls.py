from django.urls import path
from .views import *


urlpatterns = [

    path('', index, name='shop'),
    path('search/', search, name='search'),
    path('cart/', cart, name='cart'),
    path('edit_favorite/<product>/<order>', edit_favorite, name='edit_favorite'),
    path('edit_cart/<seller>/<product>/<order>', edit_cart, name='edit_cart'),
    path('product/', product, name='product'),
    path('product_filter/<order>/<id>', product_filter, name='product_filter'),
    path('shopping_complate_buy/', shopping_complate_buy, name='shopping_complate_buy'),
    path('singel_product/<id>', singel_product, name='singel_product'),

    path('single_no_product/', single_no_product, name='single_no_product'),
    path('cart_empty/', cart_empty, name='cart_empty'),
    path('shopping_no_complate_buy/', shopping_no_complate_buy, name='shopping_no_complate_buy'),

    path('about_us/', about_us, name='about_us'),
    path('contact_us/', contact_us, name='contact_us'),
    path('rules/', rules, name='rules'),

    path('payment/', payment, name='payment'),
    path('verifyStore/', verifyStore),
]
