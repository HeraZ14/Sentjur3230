from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from pyexpat.errors import messages
from store.models import Product, Customer, Cart, CartItem, Order, Category, PriceTypes, ProductPrice


# Create your views here.

def home(request):
    return render(request, 'shop/home.html',{})

def sentjur_merch(request):
    if request.method == 'POST':
        selected_info = request.POST.get('selected_info')
        return redirect('sentjur-merch')

    products = Product.objects.filter(category__name='Šentjur Merch').prefetch_related(
        Prefetch('productprice_set', queryset=ProductPrice.objects.select_related('price_type'))
    )
    priceTypes = PriceTypes.objects.all()
    return render(request, 'shop/sentjur-merch.html', {
        'products': products,
        'priceTypes': priceTypes,
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


@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    selected_info = request.POST.get('selected_info')

    if not product_id or not selected_info:
        return redirect('sentjur-merch')

    product = Product.objects.get(id=product_id)
    cart = request.session.get('cart', [])

    # Preveri, če tak produkt + cena že obstaja
    found = False
    for item in cart:
        if (str(item['product_id']) == str(product.id)
                and item['price_info'] == selected_info):
            item['quantity'] += 1
            found = True
            break

    if not found:
        cart.append({
            'product_id': product.id,
            'product_name': product.name,
            'price_info': selected_info,
            'quantity': 1,
        })

    request.session['cart'] = cart
    return redirect('sentjur-merch')



@require_POST
def remove_from_cart(request):
        product_id = request.POST.get('product_id')
        price_info = request.POST.get('price_info')

        cart = request.session.get('cart', [])

        updated_cart = []
        for item in cart:
            if (str(item['product_id']) == str(product_id)
                    and item['price_info'] == price_info):
                if item['quantity'] > 1:
                    item['quantity'] -= 1
                    updated_cart.append(item)
                # Else: ne dodamo več (kar pomeni, da ga izbrišemo)
            else:
                updated_cart.append(item)

        request.session['cart'] = updated_cart
        return redirect('vojzek')

@require_POST
def update_cart(request):
    product_id = request.POST.get('product_id')
    price_info = request.POST.get('price_info')
    quantity = request.POST.get('quantity')

    try:
        quantity = int(quantity)
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        return redirect('vojzek')  # Neveljavna količina, nič ne spremeni

    cart = request.session.get('cart', [])
    for item in cart:
        if (str(item['product_id']) == str(product_id)
                and item['price_info'] == price_info):
            item['quantity'] = quantity
            break

    request.session['cart'] = cart
    return redirect('vojzek')


def cart_view(request):
    cart = request.session.get('cart', [])

    total_price = 0
    for item in cart:
        item_price = float(item['price_info'].split(' ')[-1])
        item_total = item_price * item['quantity']
        item['price_per_unit'] = item_price
        item['total_price'] = item_total
        total_price += item_total

    context = {
        'cart': cart,
        'total_price': total_price,
    }
    return render(request, 'shop/vojzek.html',context)