from django.shortcuts import render, get_object_or_404, redirect
from pyexpat.errors import messages
from store.models import Product, Customer, Cart, CartItem, Order, Category, PriceTypes


# Create your views here.

def home(request):
    return render(request, 'shop/home.html',{})

def sentjur_merch(request):
    products = Product.objects.filter(category__name='Šentjur Merch')
    priceTypes = PriceTypes.objects.all()
    product_prices = {}
    for product in products:
        product_prices = {
            'product': product,
            'prices': {}
        }
        for pt in priceTypes:
            price = round(product.weight * pt.price, 2)
            product_prices['prices'][pt.name] = price

    return render(request, 'shop/sentjur-merch.html', {
        'products': products,
        'priceTypes': priceTypes,
        'productPrices': product_prices,
    })

def ostali_merch(request):
    products = Product.objects.filter(category__name='Ostali Merch')
    print("Najdenih izdelkov:", products.count())
    return render(request, 'shop/ostali-merch.html', {'products':products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})


def kontakt(request):
    return render(request, 'shop/kontakt.html')

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = None

    # Preveri, ali uporabnik že ima košarico
    if request.user.is_authenticated:
        customer, created = Customer.objects.get_or_create(user=request.user)
        cart, created = Cart.objects.get_or_create(customer=customer)
    else:
        # Za neprijavljene uporabnike uporabi sejo
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)

    # Dodaj izdelek v košarico ali povečaj količino
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"{product.name} dodan v košarico!")
    return redirect('cart_detail')