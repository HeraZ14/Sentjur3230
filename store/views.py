from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from store.models import Product, Customer, Cart, CartItem, Order, Category, PriceTypes, ProductPrice, ProductSize


# Create your views here.

def sentjur_merch(request):
    if request.method == 'POST':
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
    selected_size = request.POST.get('selected_size')
    selected_price_id = request.POST.get('selected_price_id')
    if not selected_price_id or not selected_size:
        messages.warning(request, "Izpolni obvezna polja gospodič.")
        print(product_id)
        return redirect('product_detail', pk=product_id)
    selected_price_id = int(selected_price_id)
    get_price_item = ProductPrice.objects.get(id=selected_price_id)
    price_item = str(get_price_item.price)




    #product_size = ProductSize.objects.get(product=product, size=size)
    #if quantity_requested > product_size.quantity:
    #    messages.error(request, "Na voljo je samo še {} kosov.".format(product_size.quantity))
    #    return redirect('product_detail', pk=product.id)

    product = Product.objects.get(id=product_id)
    cart = request.session.get('cart', [])

    # Preveri, če tak produkt + cena že obstaja
    found = False
    for item in cart:
        if (str(item['product_id']) == str(product.id)
                and item['selected_price_id'] == selected_price_id):
            item['quantity'] += 1
            found = True
            break

    if not found:
        cart.append({
            'product_id': product.id,
            'product_name': product.name,
            'selected_price_id':selected_price_id,
            'price_item': price_item,
            'quantity': 1,
        })

    request.session['cart'] = cart
    return redirect('sentjur-merch')



@require_POST
def remove_from_cart(request):
        product_id = request.POST.get('product_id')
        selected_price_id = int(request.POST.get('selected_price_id'))

        cart = request.session.get('cart', [])

        updated_cart = []
        for item in cart:
            if (str(item['product_id']) == str(product_id)
                    and item['selected_price_id'] == selected_price_id):
                if item['quantity'] > 0:
                    item['quantity'] = 0
                # Else: ne dodamo več (kar pomeni, da ga izbrišemo)
            else:
                updated_cart.append(item)

        request.session['cart'] = updated_cart
        return redirect('vojzek')

@require_POST
def update_cart(request):
    product_id = request.POST.get('product_id')
    selected_price_id = int(request.POST.get('selected_price_id'))
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
                and item['selected_price_id'] == selected_price_id):
            item['quantity'] = quantity
            break

    request.session['cart'] = cart
    return redirect('vojzek')


def cart_view(request):
    cart = request.session.get('cart', [])

    total_price = 0
    for item in cart:
        print(item['price_item'])
        item_price = float(item['price_item'])
        item_total = item_price * item['quantity']
        item['price_per_unit'] = item_price
        item['total_price'] = item_total
        total_price += item_total

    context = {
        'cart': cart,
        'total_price': total_price,
    }
    return render(request, 'shop/vojzek.html',context)