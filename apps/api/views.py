import random
from uuid import UUID
from django.core import serializers
from kavenegar import *
from django.views.decorators.csrf import csrf_exempt
from django.http import *
from django.shortcuts import redirect
from zeep import Client
from shop.models import *


@csrf_exempt
def notification(request):
    id = request.POST.get('id')
    exist = Store.objects.filter(id=id)
    if exist:
        status = "200"
        return JsonResponse({'status': status, 'data': get_store(UUID(id))})
    else:
        data = {}
        status = "404"
        return JsonResponse({'status': status, 'data': data})


def get_store(token):
    user = Store.objects.filter(id=token)
    data = list(user.values())[0]
    data['state_id'] = list(State.objects.filter(id=data['state_id']).values())[0] if data['state_id'] else None
    return data


@csrf_exempt
def verify(request):
    code = str(random.randint(10000, 99999))
    phone = request.POST.get('phone')
    if phone:
        exist = Store.objects.filter(phone=phone)
        api = KavenegarAPI('5A64303148383755315336324858477A7A5630764C7357486C44493238743353')
        params = {
            'sender': '',  # optinal
            'receptor': phone,  # multiple mobile number, split by comma
            'message': f" مشترک گرامی کد تایید آسونا شما : {code}",
        }
        api.sms_send(params)
        status = "200"
        if exist:
            exist.update(code=code)
        return JsonResponse({'status': status,
                             'code': code, 'phone': phone})

    else:
        print("Phone Is Empty", 'phone : ' + phone)
        status = "Phone Is Empty"
        return JsonResponse({'status': status})


@csrf_exempt
def verify_code(request):
    phone = request.POST.get('phone')
    code = request.POST.get('code')
    store = Store.objects.filter(phone=phone,code=code)
    if phone:
        return JsonResponse({'status': "200" if store else "404",
                             'code': code,
                             'data': get_store(store.first().id) if store else None})
    else:
        status = "Phone Is Empty"
        print(status)
        return JsonResponse({'status': status})


@csrf_exempt
def sing_up(request):
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    shop_name = request.POST.get('shop_name')
    phone = request.POST.get('phone')
    address = request.POST.get('address')
    national_code = request.POST.get('national_code')

    if phone:
        exist = Store.objects.filter(phone=phone)
        if not exist:
            if first_name and last_name and shop_name and phone and address and national_code:
                model = Store.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    shop_name=shop_name,
                    phone=phone,
                    address=address,
                    national_code=national_code
                )
                data = get_store(model.id)
                status = "201"
                print("Store Created")
                return JsonResponse({'status': status, 'data': data})
            else:
                status = "One Store Data Is Empty"
                print(status)
                return JsonResponse({'status': status})
        else:
            status = "Store Found"
            print(status)
            return JsonResponse({'status': status})
    else:
        status = "Phone Is Empty"
        print(status)
        return JsonResponse({'status': status})


@csrf_exempt
def index(request):
    data = []
    slider = Slider.objects.all()[:5]
    category = Category.objects.filter(mother=None)[:9]
    product = Product.objects.all()[:10]
    brand = Distribution.objects.filter(showing=True)[:10]
    data.append({'id': '', 'type': 'slider', 'data': list(slider.values())})
    data.append({'id': '', 'type': 'category', 'data': list(category.values())})
    data.append({'id': '', 'type': 'product', 'data': {'list': list(product.values()),
                                                       'title': 'مناسبتی ها'}})
    data.append({'id': '', 'type': 'distribution', 'data': list(brand.values())})

    return JsonResponse(data, safe=False)


@csrf_exempt
def show_all(request):
    distribution = request.POST.get('distribution')

    if distribution:
        lis = Distribution.objects.filter(category__distribution__id__in=[distribution]).values_list('category')
        category = Category.objects.filter(id__in=lis, mother=None)
    else:
        category = Category.objects.filter(mother=None)

    data = list(category.values())
    return JsonResponse(data, safe=False)


@csrf_exempt
def category(request):
    id = request.POST.get('id')
    limit = request.POST.get('limit')

    distribution = json.loads(request.POST.get('distribution'))

    if distribution:
        lis = Distribution.objects.filter(id__in=distribution).values_list('category')
        category = Category.objects.filter(id__in=lis, mother_id=id)
    else:
        category = Category.objects.filter(mother_id=id)

    if category:
        data = list(category.values())
        distributions = Distribution.objects.filter(category__id__in=[id])
        distributions = list(distributions.values())
        data = {'data': data, 'type': 'category','distributions':distributions}
    else:
        filter = {'category_id': id}
        users = Distribution.objects.filter(id__in=distribution).values_list('user')
        print(users)
        if distribution:
            filter['seller__id__in'] = users
        if limit:
            category__ = Product.objects.filter(**filter)[0:int(limit)]
        else:
            category__ = Product.objects.filter(**filter)
        data = list(category__.values())
        data = {'data': data, 'type': 'product'}
    return JsonResponse(data, safe=False)


@csrf_exempt
def product(request):
    id = request.POST.get('id')
    limit = request.POST.get('limit')
    distribution = request.POST.get('distribution')
    filter = {'category_id': id}
    if distribution:
        filter['seller_id'] = distribution
    if limit:
        category__ = Product.objects.filter(**filter)[0:int(limit)]
    else:
        category__ = Product.objects.filter(**filter)
    data = list(category__.values())
    data = {'data': data, 'type': 'product'}
    return JsonResponse(data, safe=False)


@csrf_exempt
def distribution(request):
    id = request.POST.get('id')
    limit = request.POST.get('limit')
    if limit:
        category__ = Distribution.objects.filter(id=id)[0:int(limit)]
    else:
        category__ = Distribution.objects.filter(id=id)

    data = list(category__.values())
    return JsonResponse(data, safe=False)


@csrf_exempt
def detail(request):
    id = request.POST.get('id')
    user = request.POST.get('store')

    product = Product.objects.filter(id=id)
    description = ProductDescription.objects.filter(product_id=id)
    image = ProductImage.objects.filter(product_id=id)

    data = list(product.values())[0]
    data['images'] = list(image.values())
    data['descriptions'] = list(description.values())
    data['seller_id'] = json.loads(
        serializers.serialize('json', [Distribution.objects.get(user_id=product[0].seller.id)], ensure_ascii=False)[
        1:-1])

    cart = Cart.objects.filter(buyer=user, product=id)
    data['isCart'] = True if cart else False

    fav = Favorite.objects.filter(user=user, product=id)
    data['isFav'] = True if fav else False

    return JsonResponse(data, safe=False)


@csrf_exempt
def cart(request):
    product = request.POST.get('product')
    store = request.POST.get('store')
    number = request.POST.get('number')
    order = request.POST.get('order')

    if order == "get" and store:
        cart = Cart.objects.filter(buyer=store)
        data = list(cart.values())
        for item in data:
            product_object = Product.objects.filter(id=item['product_id'])
            distribution = Distribution.objects.filter(id=product_object[0].seller.id)

            item['product_id'] = list(product_object.values())[0]
            item['distribution'] = list(distribution.values())[0] if distribution else {}
    elif order == "add" and product and store and number:

        exist, arg2 = Cart.objects.update_or_create(product_id=product, buyer_id=store,
                                                    defaults={'number': number})
        if exist:
            data = {"status": 200}
        else:
            data = {"status": 404}

    elif order == "delete" and store and product:
        cart = Cart.objects.filter(buyer=store, product=product).delete()
        if cart:
            data = {"status": 200}
        else:
            data = {"status": 404}

    else:
        print("order is : " + order)
        data = {"status": 'Order Not Found'}

    return JsonResponse(data, safe=False)


@csrf_exempt
def favorite(request):
    product = request.POST.get('product')
    user = request.POST.get('store')
    order = request.POST.get('order')

    if order == "get" and user:
        favorite = Favorite.objects.filter(user=user)
        list_favorite_product = favorite.values_list("product__id", flat=True)
        favorite_product = Product.objects.filter(id__in=list_favorite_product)
        data = list(favorite_product.values())

    elif order == "add" and product and user:
        prof = Store.objects.get(id=user)
        prod = Product.objects.get(id=product)

        exist = Favorite.objects.filter(product=prod, user=prof)
        if not exist:
            Favorite.objects.create(product=prod, user=prof)
            data = {"status": 200}
        else:
            data = {"status": 404}

    elif order == "delete" and user and product:
        fave = Favorite.objects.filter(user=user, product=product).delete()
        if fave:
            data = {"status": 200}
        else:
            data = {"status": 404}

    else:
        data = {"status": 'Order Not Found'}

    return JsonResponse(data, safe=False)


@csrf_exempt
def store(request):
    token = request.POST.get('token')
    order = request.POST.get('order')
    data = request.POST.get('data')

    if order == "update" and token:
        data = json.loads(data)
        if 'state' in data:
            data['state'] = State.objects.get(id=data['state'])
        store, ras = Store.objects.update_or_create(id=token, defaults=data)
        data = get_store(store.id)
    elif order == "get" and token:
        data = get_store(token)
        return JsonResponse(data, safe=False)
    else:
        return HttpResponseNotFound({'status': 404})

    return JsonResponse(data, safe=False)


@csrf_exempt
def state(request):
    state = State.objects.filter(mother=None)
    data = list(state.values())
    for city in data:
        city['city'] = list(State.objects.filter(mother=city['id']).values())
    return JsonResponse(data, safe=False)


@csrf_exempt
def distribution(request):
    state = State.objects.filter(mother=None)
    data = list(state.values())
    for city in data:
        city['city'] = list(State.objects.filter(mother=city['id']).values())
    return JsonResponse(data, safe=False)


@csrf_exempt
def payment(request):
    MERCHANT = '516b2600-244a-11e9-a2a5-005056a205be'
    client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
    user = request.GET.get('store')
    amount = 0  # Toman / Required
    description = "خرید از آسونا"  # Required

    CallbackURL = 'http://185.110.190.106/api/verify_payment/' + user  # Important: need to edit for realy server.

    for item in Cart.objects.filter(buyer=user):
        amount += item.product.price * item.number

    result = client.service.PaymentRequest(MERCHANT, amount, description, '', '', CallbackURL)

    if result.Status == 100:
        return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
    else:
        return HttpResponse('Error code: ' + str(result.Status))


@csrf_exempt
def verify_payment(request, user):
    MERCHANT = '516b2600-244a-11e9-a2a5-005056a205be'
    client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')

    if request.GET.get('Status') == 'OK':
        result = client.service.PaymentVerification(MERCHANT, request.GET['Authority'], 1000)
        product_list = []

        for item in Cart.objects.filter(buyer_id=user):
            product_list.append(item.id)

        Order.objects.create(
            product=product_list,
            buyer_id=user,
            status='payment',
            payment=1
        )

        return HttpResponse(result.Status)
    else:
        return HttpResponse(MERCHANT)


@csrf_exempt
def add_order(request):
    user = request.POST.get('store')
    product_list = []
    price = 0

    for item in Cart.objects.filter(buyer_id=user):
        product_list.append(item.id)
        price += item.product.price * item.number

    result = Order.objects.create(
        buyer_id=user,
        status='payment',
        payment=0,
        price=price
    )
    result.product.set(product_list)

    if result:
        Cart.objects.filter(buyer_id=user).delete()
        return JsonResponse({'status': 200})

    else:
        return HttpResponse({'status': 404})


@csrf_exempt
def order(request):
    user = request.POST.get('store')

    order = Order.objects.filter(buyer_id=user)
    data_0 = list(order.values())
    for item_0 in order:
        carts = item_0.product.all()
        data_1 = list(carts.values())
        for cart in data_1:
            product_object = Product.objects.filter(id=cart['product_id'])
            distribution = Distribution.objects.filter(id=product_object[0].seller.id)
            cart['product_id'] = list(product_object.values())[0]
            cart['distribution'] = list(distribution.values())[0]
        for item in data_0:
            if item['id'] == item_0.id:
                item['product'] = data_1
    return JsonResponse(data_0, safe=False)


@csrf_exempt
def test(request):
    return HttpResponse("Test")
