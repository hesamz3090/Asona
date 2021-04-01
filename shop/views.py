from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from uuid import UUID
from shop.models import *
from django.http import *
from django.db.models import Q
from django.shortcuts import redirect
from zeep import Client


def index(request):
    slider = Slider.objects.all()[:5]
    category = Category.objects.filter(showing=True)[:9]
    product = Product.objects.filter(offer__gte=0)[:10]
    distribution = Distribution.objects.filter(showing=True)[:10]
    return render(request, 'shop/index.html', {
        'slider': slider,
        'category': category,
        'distribution': distribution,
        'product': product,
    })


def search(request):
    search = request.POST.get('search')
    if request.method == 'POST' and search:
        product = Product.objects.filter(Q(title_fa__icontains=search) | Q(title_en__icontains=search))
        category = Category.objects.filter(Q(name__icontains=search))
        distribution = Distribution.objects.filter(Q(name__icontains=search))
        return render(request, 'shop/search.html',
                      {'product': product, 'category': category, 'distribution': distribution})
    else:
        return render(request, 'shop/404.html', {})


def cart(request):
    store = request.COOKIES['id']
    cart = Cart.objects.filter(buyer=store, status='cart')
    count = cart.count()
    total_price = 0
    for item in cart:
        total_price += item.number * item.product.price
    response = render(request, 'shop/cart.html', {'cart': cart, 'total_price': total_price, 'count': count})

    if request.GET.get('number'):
        number = request.GET.get('number')
        cart_id = request.GET.get('cart_id')
        Cart.objects.filter(id=cart_id).update(number=number)

    return response


def edit_cart(request, seller, product, order):
    id = request.COOKIES['id']
    if id:
        if order == "delete":
            Cart.objects.filter(buyer_id=id, product_id=product).delete()
            response = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        elif order == "add":
            Cart.objects.create(buyer_id=id, product_id=product, status='cart', seller_id=seller)
            response = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            response = HttpResponseNotFound()
    else:
        response = HttpResponseNotFound()
    return response


def edit_favorite(request, product, order):
    id = request.COOKIES['id']
    if id:
        if order == "delete":
            Favorite.objects.filter(user_id=id, product_id=product).delete()
            response = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        elif order == "add":
            Favorite.objects.create(user_id=id, product_id=product)
            response = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            response = HttpResponseNotFound()
    else:
        response = HttpResponseNotFound()
    return response


def product(request):
    product_newest = Product.objects.all().order_by('created_date')
    product_expensive = Product.objects.all().order_by('price')
    product_cheep = Product.objects.all().order_by('-price')
    category = Category.objects.all()[:9]
    product = Product.objects.all()[:10]
    distribution = Distribution.objects.filter(status=True)[:10]
    return render(request, 'shop/product.html', {
        'product_newest': product_newest,
        'product_expensive': product_expensive,
        'product_cheep': product_cheep,
        'category': category,
        'product': product,
        'distribution': distribution,
    })


def product_filter(request, order, id):
    if order == 'search':
        item = Product.objects.filter(name__search=id)

    elif order == 'category':
        item = Product.objects.filter(category_id=id)

    elif order == 'distribution':
        distribution = Distribution.objects.filter(id=id)
        id_list = distribution.values_list("id", flat=True)
        item = Product.objects.filter(id__in=id_list)

    else:
        item = Product.objects.all()

    product_newest = item.order_by('created_date')
    product_expensive = item.all().order_by('price')
    product_cheep = item.order_by('-price')

    category = Category.objects.all()[:10]
    distribution = Distribution.objects.all()[:10]

    return render(request, 'shop/product.html', {
        'product_newest': product_newest,
        'product_expensive': product_expensive,
        'product_cheep': product_cheep,
        'category': category,
        'distribution': distribution,
    })


def shopping_complate_buy(request):
    return render(request, 'shop/shopping-complate-buy.html', {})


def singel_product(request, id):
    store = request.COOKIES.get('id')

    product = Product.objects.get(id=UUID(id))
    image = ProductImage.objects.filter(product_id=UUID(id))
    description = ProductDescription.objects.filter(product_id=UUID(id))

    Isfave = Favorite.objects.filter(user_id=store, product_id=id)
    Iscart = Cart.objects.filter(buyer_id=store, product_id=id)
    return render(request, 'shop/single-product.html', {
        'product': product,
        'image': image,
        'description': description,
        'store': store,
        'Isfave': Isfave,
        'Iscart': Iscart
    })


def single_no_product(request):
    return render(request, 'shop/single-no-product.html', {})


def cart_empty(request):
    return render(request, 'shop/cart-empty.html', {})


def shopping_no_complate_buy(request):
    return render(request, 'shop/shopping-no-complate-buy.html', {})


def about_us(request):
    distribution = Distribution.objects.filter(status=True)[:10]
    return render(request, 'shop/about_us.html', {'distribution': distribution})


def contact_us(request):
    return render(request, 'shop/contact_us.html', {})


def rules(request):
    return render(request, 'shop/rules.html', {})


def page_404(request, exception):
    return render(request, 'shop/404.html', {})


def send_request(price, store):
    MERCHANT = '516b2600-244a-11e9-a2a5-005056a205be'
    client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
    amount = price  # Toman / Required
    description = "ثبت سفارش در آسونا"  # Required
    email = 'email@example.com'  # Optional
    mobile = '09123456789'  # Optional
    CallbackURL = 'http://127.0.0.1:8000/verifyStore/' + store

    result = client.service.PaymentRequest(MERCHANT, amount, description, email, mobile, CallbackURL)
    if result.Status == 100:
        return 'https://www.zarinpal.com/pg/StartPay/' + str(result.Authority)
        # return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
    else:
        print(str(result.Status))
        return HttpResponse('Error code: ' + str(result.Status))


def verifyStore(request, store):
    MERCHANT = '516b2600-244a-11e9-a2a5-005056a205be'
    client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')

    if request.GET.get('Status') == 'OK':
        result = client.service.PaymentVerification(MERCHANT, request.GET['Authority'], 1000)
        return HttpResponse(result.Status)
    else:
        return HttpResponse(MERCHANT)


def payment(request):
    price = request.GET.get('price')
    type = request.GET.get('type')
    if type == "online":
        store = request.COOKIES.get('id')
        response = HttpResponseRedirect(send_request(price, store))
    else:
        order = Order.objects.create()
        response = HttpResponse("Offline")
    return response
