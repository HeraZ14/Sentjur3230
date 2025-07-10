import json

import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from store.models import Product, Cart, CartItem, Category, PriceTypes, ProductPrice, ProductSize, Order, OrderItem, StripeLogs


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
    cart = request.session.get('cart', [])
    return render(request, 'shop/checkout.html', {'cart': cart})


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        metadata = intent.get('metadata', {})
        order_id = metadata.get('order_id')
        email = intent.get('receipt_email')

        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.status = True
                payment_method_id = intent.get('payment_method')
                if payment_method_id:
                    method = stripe.PaymentMethod.retrieve(payment_method_id)
                    order.payment_method = method.type
                order.save()
                if email:
                    send_mail(
                        subject='Plačilo uspešno',
                        message='Vaše naročilo je bilo uspešno plačano. Hvala!',
                        from_email='no-reply@tvoja-domena.si',
                        recipient_list=[email],
                        fail_silently=True,
                    )
                print(f"✅ Naročilo {order_id} za {email} uspešno plačano (Elements).")
                stripe_logs_create(event['id'], event['type'], order, event, True)
            except Order.DoesNotExist:
                print(f"⚠️ Naročilo z ID {order_id} ni najdeno.")
                stripe_logs_create(event['id'], event['type'], None, event, False)

    elif event['type'] == 'payment_intent.payment_failed':
        intent = event['data']['object']
        metadata = intent.get('metadata', {})
        order_id = metadata.get('order_id')
        error_message = intent.get('last_payment_error', {}).get('message', 'Ni sporočila.')

        print(f"❌ Plačilo spodletelo za naročilo {order_id}: {error_message}")
        stripe_logs_create(event['id'], event['type'], None, event, False)
        
    elif event['type'] == 'payment_intent.processing':
        intent = event['data']['object']
        order_id = intent.get('metadata', {}).get('order_id')
        print(f"⏳ Plačilo za naročilo {order_id} je v obdelavi (processing).")
        stripe_logs_create(event['id'], event['type'], None, event, True)

    return HttpResponse(status=200)

def payment_success(request):
    if 'cart' in request.session:
        del request.session['cart']
    messages.success(request, "Naročilo je bilo uspešno oddano. Preveri email.")
    return redirect('home')

def payment_cancel(request):
    messages.warning(request, "Plačilo je bilo preklicano.")
    return redirect('home')


def stripe_logs_create(event_id, event_type, order, event, payment_intent):
    StripeLogs.objects.create(
        event_id=event_id,
        event_type=event_type,
        order_id=order,
        payload=json.dumps(event),
        processed_successfully=payment_intent
    )

@csrf_exempt
def create_payment_intent(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    # CSRF je že poslan prek Fetch z headerjem, zato lahko uporabljamo request.POST
    email = request.POST.get('email')
    address = request.POST.get('address')
    phone = request.POST.get('phone')

    if not email or not address or not phone:
        return JsonResponse({'error': 'Vsa polja so obvezna.'}, status=400)

    cart = request.session.get('cart', [])
    if not cart:
        return JsonResponse({'error': 'Košarica je prazna.'}, status=400)

    user = request.user if request.user.is_authenticated else None

    total_amount = 0
    for item in cart:
        price = ProductPrice.objects.get(id=item['selected_price_id'])
        total_amount += int(price.price * 100) * item['quantity']

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

    try:
        intent = stripe.PaymentIntent.create(
            amount=total_amount,
            currency='eur',
            metadata={'order_id': str(order.id)},
            receipt_email=email,
            payment_method_types=[
                'card',
                'sepa_debit',
                'paypal',
                'revolut_pay',
                # Dodaj po potrebi – preveri v dashboardu, kaj imaš omogočeno
            ]
        )
        return JsonResponse({'client_secret': intent.client_secret})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def stripe_pay(request):
    client_secret = request.GET.get('client_secret')

    return render(request, 'shop/stripe_pay.html', {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'client_secret': client_secret
    })
