from django.contrib import admin
from .models import *


class ProductImage(admin.StackedInline):
    model = ProductImage


class ProductDescription(admin.StackedInline):
    model = ProductDescription


@admin.register(State)
class State(admin.ModelAdmin):
    pass


@admin.register(Store)
class Shop(admin.ModelAdmin):
    pass


@admin.register(Distribution)
class Distribution(admin.ModelAdmin):
    pass


@admin.register(Cart)
class Cart(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(Cart, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(seller=request.user)


@admin.register(Order)
class Order(admin.ModelAdmin):
    pass


@admin.register(Favorite)
class Favorite(admin.ModelAdmin):
    pass


@admin.register(Slider)
class Slider(admin.ModelAdmin):
    pass


@admin.register(Category)
class Category(admin.ModelAdmin):
    pass


@admin.register(Product)
class Product(admin.ModelAdmin):
    inlines = [ProductImage, ProductDescription]

    class Meta:
        model = Product

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.seller = request.user
        instance.save()
        form.save_m2m()
        return instance
