from django.urls import path
from .views import *

handler404 = 'apps.store.views.page_404'

urlpatterns = [

    path('', index, name='store'),
    path('order/', order, name='order'),
    path('edit/', edit, name='edit'),
    path('favorites/', favorites, name='favorites'),
    path('edit/', edit, name='edit'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', register, name='register'),
    path('code/', code, name='code'),

]
