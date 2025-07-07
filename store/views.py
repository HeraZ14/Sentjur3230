import json

import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Prefetch
from django.http import HttpResponse
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
        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card','sepa_debit'],
                line_items=[
                    {
                        'price': ProductPrice.objects.get(id=item['selected_price_id']).stripe_price_id,
                        'quantity': item['quantity'],
                    }
                    for item in cart
                ],
                mode='payment',
                success_url=request.build_absolute_uri('/success/'),
                cancel_url=request.build_absolute_uri('/cancel/'),
                client_reference_id=str(order.id),
                customer_email=email,
            )
            send_mail(
                subject='Potrditev naročila',
                message=f"Hvala za naročilo. Število artiklov: {len(cart)}",
                from_email='no-reply@tvoja-domena.si',
                recipient_list=[email],
                fail_silently=True,
            )
            # Počisti košarico
            del request.session['cart']

            return redirect(checkout_session.url)  # ali kamor želiš

        except Exception as e:
            messages.error(request, f"Napaka pri povezavi s Stripe: {str(e)}")
            return render(request, 'shop/checkout.html', {'cart': cart})

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

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        email = session.get('customer_email')
        order_id = session.get('client_reference_id')

        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                payment_intent_id = session.get('payment_intent')
                payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                payment_method_id = payment_intent.payment_method
                payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
                payment_type = payment_method.type
                order.payment_method = payment_type

                #Stripe logs

                if payment_type == 'card':
                    order.status = True  # kartično plačilo je instantno potrjeno
                    print(f"✅ Naročilo {order_id} za {email} plačano s kartico.")

                elif payment_type == 'sepa_debit':
                    order.status = False  # še ne vemo, če bo SEPA uspešen
                    print(f"⏳ Naročilo {order_id} za {email} čaka SEPA potrditev.")

                else:
                    print(f"⚠️ Nepodprt način plačila: {payment_type}")

                order.save()
                stripe_logs_create(event['id'],event['type'],order,event, True)

            except Order.DoesNotExist:
                stripe_logs_create(event['id'], event['type'], None, event, False)
                print(f"⚠️ Naročilo z ID {order_id} ni bilo najdeno.")
        else:
            print(f"⚠️ Manjka client_reference_id v sessionu.")

    elif event['type'] == 'checkout.session.async_payment_succeeded': # za SEPA potrditev, delayed payment
        session = event['data']['object']
        email = session.get('customer_email')
        order_id = session.get('client_reference_id')

        if order_id:
            try:
                order = Order.objects.get(id=order_id)

                if not order.status:
                    order.status = True  # označi kot plačano samo enkrat
                    order.save()
                    stripe_logs_create(event['id'], event['type'], order, event, True)
                    print(f"✅ (ASYNC) Naročilo {order_id} za {email} je bilo uspešno plačano.")
                else:
                    print(f"ℹ️ (ASYNC) Naročilo {order_id} je že bilo označeno kot plačano.")

            except Order.DoesNotExist:
                stripe_logs_create(event['id'],event['type'],None,event, False)
                print(f"⚠️ (ASYNC) Naročilo z ID {order_id} ni bilo najdeno.")
        else:
            print(f"⚠️ (ASYNC) Manjka client_reference_id v sessionu.")

    return HttpResponse(status=200)

def payment_success(request):
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