from django.contrib.auth.models import User
from django.db import models
from uuid import uuid4
from django.utils import timezone
from django.contrib.auth.models import User


class State(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=20)
    mother = models.ForeignKey('State', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class Store(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    shop_name = models.CharField(max_length=80, blank=True, null=True)
    first_name = models.CharField(max_length=80, blank=True, null=True)
    last_name = models.CharField(max_length=80, blank=True, null=True)
    phone = models.BigIntegerField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    national_code = models.CharField(max_length=15, blank=True, null=True)
    state = models.ForeignKey('State', on_delete=models.CASCADE, blank=True, null=True)
    locations = models.JSONField(blank=True, null=True)
    code = models.CharField(max_length=5)

    def __str__(self):
        return self.shop_name


class Distribution(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    user = models.OneToOneField(User, related_name='distribution', on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    category = models.ManyToManyField('Category')
    image = models.ImageField(upload_to='shop/distribution/')
    phone = models.BigIntegerField(blank=True, null=True)
    address = models.TextField(blank=True)
    permission = models.CharField(max_length=15, blank=True)
    showing = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Cart(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    cart_status = (
        ('cart', 'cart'),
        ('payment', 'payment'),
        ('process', 'process'),
        ('send', 'send'),
        ('receive', 'receive'),
    )
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    buyer = models.ForeignKey('Store', on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.IntegerField(default=1)
    date = models.IntegerField(default=0)
    status = models.CharField(choices=cart_status, max_length=7)

    def save(self, *args, **kwargs):
        self.seller = self.product.seller
        super(Cart, self).save(*args, **kwargs)


class Order(models.Model):
    order_status = (
        ('cart', 'cart'),
        ('payment', 'payment'),
        ('process', 'process'),
        ('send', 'send'),
        ('receive', 'receive'),
    )

    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    product = models.ManyToManyField('Cart')
    buyer = models.ForeignKey('Store', on_delete=models.CASCADE)
    price = models.BigIntegerField()
    status = models.CharField(choices=order_status, max_length=7)
    payment = models.BooleanField(default=False)
    date = models.IntegerField(default=0)
    payment_code = models.BigIntegerField(default=0)


class Favorite(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(Store, default=None, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', default=None, on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name


class Slider(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=20)
    image = models.ImageField(upload_to='shop/slide')


class Category(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=80)
    mother = models.ForeignKey('Category', on_delete=models.CASCADE, blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(upload_to='shop/category', blank=True, null=True)
    Offer = models.IntegerField(default=0)
    showing = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    types = (
        ('0', 'کیلو'),
        ('1', 'لیتر'),
        ('2', 'گرم'),
        ('3', 'بسته'),
        ('5', 'کارتون'),
        ('6', 'کیسه'),
        ('7', 'شل'),
        ('8', 'عدد'),
    )
    created_date = models.DateTimeField('date created', default=timezone.now, editable=False)
    name = models.CharField(max_length=80)
    description = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    price = models.BigIntegerField()
    profit = models.BigIntegerField()
    image = models.FileField(blank=True, upload_to='shop/product/')
    type = models.CharField(choices=types, max_length=1)
    number = models.IntegerField()
    max = models.IntegerField()
    min = models.IntegerField()
    step = models.IntegerField()
    seller = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, editable=False)
    offer = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    product = models.ForeignKey('Product', default=None, on_delete=models.CASCADE)
    images = models.FileField(upload_to='shop/product/')

    def __str__(self):
        return self.product.name


class ProductDescription(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    product = models.ForeignKey('Product', default=None, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50)

    def __str__(self):
        return self.product.name
