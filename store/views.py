from django.shortcuts import render

from store.models import Product


# Create your views here.

def home(request):
    return render(request, 'shop/home.html',{})

def sentjur_merch(request):
    products = Product.objects.all()
    print("Najdenih izdelkov:", products.count())
    return render(request, 'shop/sentjur-merch.html', {'products':products})
