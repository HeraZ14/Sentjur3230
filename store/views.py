from django.core.mail import send_mail
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from store.models import Product, Cart, CartItem, Category, PriceTypes, ProductPrice, ProductSize, Order, OrderItem


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



def smarski_merch(request):
    products = Product.objects.filter(category__name='Šmarski Merch')
    return render(request, 'zajebancija/glasovanje.html', {'products':products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})


def kontakt(request):
    return render(request, 'shop/kontakt.html')


@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    selected_size_id = request.POST.get('selected_size_id')
    selected_price_id = request.POST.get('selected_price_id')
    selected_quantity = request.POST.get('selected_quantity')
    if not selected_price_id or not selected_size_id:
        messages.warning(request, "Izpolni obvezna polja gospodič.")

        product = get_object_or_404(Product, pk=product_id)

        return render(request, 'shop/product_detail.html', {
            "product": product,
            "selected_price_id": selected_price_id,
            "selected_size_id": selected_size_id,
            "selected_quantity": selected_quantity,
        })

    selected_price_id = int(selected_price_id)
    try:
        get_price_item = ProductPrice.objects.get(id=selected_price_id, product_id=product_id)
    except ProductPrice.DoesNotExist:
        messages.error(request, "Že tak je čist zapstoj, pa še bi se muzljal. Tako ja, udrihaj bo ubogem človeku.")
        return redirect('product_detail', pk=product_id)
    price_item = str(get_price_item.price)

    ###Preverjamo Zalogo + če izdelka ni v košarici, ga dodamo z selected_quantity,
    ###Če pa izdelek je v košarici mu samo povečamo količino.
    product = Product.objects.get(id=product_id)
    cart = request.session.get('cart', [])
    get_available_stock = ProductSize.objects.get(product_id=product.id, size_id=selected_size_id)
    available_stock = get_available_stock.quantity

    # Preveri, če tak produkt + cena že obstaja + če je dovolj zaloge
    found = False
    same_item_quantity = 0
    for item in cart:
        if str(item['product_id']) == str(product.id):
            if item['selected_price_id'] == selected_price_id:
                item['quantity'] += int(selected_quantity)
                found = True
            print('začetek f: ', same_item_quantity)
            same_item_quantity += int(item['quantity'])
            print('Konec f: ',same_item_quantity)

        if available_stock < int(selected_quantity) + same_item_quantity:
            messages.error(request, f"Na voljo je samo še {available_stock} kosov.")
            return redirect('product_detail', pk=product_id)



    if not found:
        if available_stock >= int(selected_quantity):
            cart.append({
                'product_id': product.id,
                'product_name': product.name,
                'selected_price_id':selected_price_id,
                'selected_size_id':selected_size_id,
                'price_item': price_item,
                'quantity': int(selected_quantity),
                'image_url': product.image.url if product.image else '',
            })
        else:
            messages.error(request, f"Na voljo je samo še {available_stock} kosov.")
            return redirect('product_detail', pk=product_id)

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
    selected_quantity = request.POST.get('selected_quantity')
    selected_size_id = request.POST.get('selected_size_id')

    get_available_stock = ProductSize.objects.get(product_id=product_id, size_id=selected_size_id)
    available_stock = get_available_stock.quantity

    try:
        selected_quantity = int(selected_quantity)
        if selected_quantity < 1:
            selected_quantity = 1
    except (ValueError, TypeError):
        return redirect('vojzek')  # Neveljavna količina, nič ne spremeni

    cart = request.session.get('cart', [])
    same_item_quantity = 0
    for item in cart:
        if str(item['product_id']) == str(product_id):
            if item['selected_price_id'] == selected_price_id:
                item['quantity'] = selected_quantity
            else:
                same_item_quantity += int(item['quantity'])

        if selected_quantity + same_item_quantity > available_stock:
            messages.error(request, f"Na voljo je samo še {available_stock} kosov.")
            return redirect('vojzek')

    request.session['cart'] = cart
    return redirect('vojzek')


def cart_view(request):
    cart = request.session.get('cart', [])

    total_price = 0
    for item in cart:
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


#CHECKOUT

def get_cart_items(request):
    if request.user.is_authenticated:
        return CartItem.objects.filter(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        return CartItem.objects.filter(session_key=session_key)


def checkout(request):
    session_key = request.session.session_key

    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart = request.session.get('cart', [])

    if request.method == 'POST':
        user = request.user if request.user.is_authenticated else None
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        if not email or not address:
            messages.error(request, "Vsa polja so obvezna.")
            return render(request, 'shop/checkout.html', {'cart': cart})

        order = Order.objects.create(
            user=user,
            email=email,
            address=address,
            phone=phone,
            status=False
        )

        for item in cart:
            product = Product.objects.get(id=item['product_id'])
            price = ProductPrice.objects.get(id=item['selected_price_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price=price,

            )

        # Pošlji email (zaenkrat na konzolo)
        send_mail(
            subject='Potrditev naročila',
            message=f"Hvala za naročilo. Število artiklov: {len(cart)}",
            from_email='no-reply@tvoja-domena.si',
            recipient_list=[email],
            fail_silently=True,
        )

        # Počisti košarico
        del request.session['cart']

        messages.success(request, "Naročilo je bilo uspešno oddano. Preveri email.")
        return redirect('home')  # ali kamor želiš

    return render(request, 'shop/checkout.html', {'cart': cart})