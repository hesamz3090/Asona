from django.shortcuts import render
from shop.models import *
from kavenegar import *
from random import *
from django.http import HttpResponseServerError, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect


def index(request):
    id = request.COOKIES['id']
    order = Order.objects.filter(buyer=id)
    profile = Store.objects.get(id=id)
    favorite = [i.product for i in Favorite.objects.filter(user=id)]
    return render(request, 'store/profile.html',
                  {'order': order, 'profile': profile, 'favorite': favorite})


def order(request):
    id = request.COOKIES['id']
    order = Order.objects.filter(buyer=id,status='payment')
    return render(request, 'store/order.html', {'order': order})


def favorites(request):
    id = request.COOKIES['id']
    favorite = [i.product for i in Favorite.objects.filter(user=id)]
    return render(request, 'store/favorites.html', {'favorite': favorite})


def edit(request):
    id = request.COOKIES['id']
    profile = Store.objects.get(id=id)
    activity = Category.objects.filter()

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        shop_name = request.POST.get('shop_name')
        activity = request.POST.get('activity')
        address = request.POST.get('address')
        national_code = request.POST.get('national_code')
        state = request.POST.get('state')

        exist = Store.objects.filter(id=id)
        if exist:
            update = exist.update(
                first_name=first_name,
                last_name=last_name,
                shop_name=shop_name,
                activity=activity,
                address=address,
                national_code=national_code,
                state=state
            )
            if update:
                return redirect('/user/edit')
            else:
                return HttpResponseServerError("خطا در ثبت داده")
        else:
            return HttpResponseServerError("خطا در ثبت داده")
    return render(request, 'store/edit.html', {'profile': profile, 'activity': activity})


def login(request):
    # id = request.COOKIES['id']
    # if id:
    #     return HttpResponseRedirect('/profile/')
    #
    # elif request.method == 'POST':
    if request.method == 'POST':
        phone = request.POST.get('phone')
        code = str(randint(10000, 99999))
        phone = "98" + phone.lstrip('0')
        exist = Store.objects.filter(phone=phone)
        if exist:
            Store.objects.filter(phone=phone).update(code=code)
            api = KavenegarAPI('5A64303148383755315336324858477A7A5630764C7357486C44493238743353')
            params = {
                'sender': '',  # optinal
                'receptor': phone,  # multiple mobile number, split by comma
                'message': f" مشترک گرامی کد تایید آسونا شما : {code}",
            }
            try:
                api.sms_send(params)
                return render(request, 'store/code.html', {})
            except APIException as err:
                return HttpResponseServerError("شماره تماس اشتباه است")

        else:
            return render(request, 'store/register.html', {})

    else:
        return render(request, 'store/login.html', {})


def code(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        if code:
            try:
                data = Store.objects.get(code=code)
                id = data.id
                response = HttpResponseRedirect('/store/')
                response.set_cookie('id', id)
                return response

            except APIException as err:
                return HttpResponseServerError("کد اشتباه است")
    else:
        return render(request, 'store/login.html', {})


def register(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        national_code = request.POST.get('national_code')
        shop_name = request.POST.get('shop_name')
        address = request.POST.get('address')
        phone = f"98{phone}"
        exist = Store.objects.filter(phone=phone)
        print(first_name, last_name, shop_name, phone, address, national_code)

        if first_name and last_name and shop_name and phone and address and national_code and not exist:
            code = str(randint(10000, 99999))
            Store.objects.create(
                phone=phone,
                first_name=first_name,
                last_name=last_name,
                national_code=national_code,
                shop_name=shop_name,
                address=address,
                code=code
            )
            api = KavenegarAPI('5A64303148383755315336324858477A7A5630764C7357486C44493238743353')
            params = {
                'sender': '',  # optinal
                'receptor': phone,  # multiple mobile number, split by comma
                'message': f" مشترک گرامی کد تایید آسونا شما : {code}",
            }
            try:
                api.sms_send(params)
                return render(request, 'store/code.html', {})

            except APIException as err:
                return HttpResponseServerError("شماره اشتباه است")
        else:
            return render(request, 'store/login.html', {})
    else:
        return render(request, 'store/register.html', {})


def logout(request):
    response = render(request, 'store/login.html', {})
    response.delete_cookie('id')
    return response


def page_404(request, exception):
    return render(request, 'shop/404.html', {})
