import csv
import hashlib
import hmac
import io
import json
import logging

import stripe
from coinbase_commerce import Client
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from store.models import Product, Cart, CartItem, Category, PriceTypes, ProductPrice, ProductSize, Size, Order, OrderItem, StripeLogs, CoinbaseLogs, CheckoutForm, Newsletter
from spletka.settings import EMAIL_HOST_USER
from stripe import Invoice



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
    personalized_text = request.POST.get('personalized_text')
    if not selected_price_id or not selected_size_id:
        messages.warning(request, "Izpolni obvezna polja gospodič.")

        product = get_object_or_404(Product, pk=product_id)

        return render(request, 'shop/product_detail.html', {
            "product": product,
            "selected_price_id": selected_price_id,
            "selected_size_id": selected_size_id,
            "selected_quantity": selected_quantity,
            "personalized_text": personalized_text,
        })

    size_name = (Size.objects.get(pk=selected_size_id)).name
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
            if item['selected_price_id'] == selected_price_id and item['selected_size_id'] == selected_size_id:
                if item['personalized_text'] == personalized_text:
                    item['quantity'] += int(selected_quantity)
                    found = True
            same_item_quantity += int(item['quantity'])

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
                'size_name': size_name,
                'price_item': price_item,
                'quantity': int(selected_quantity),
                'image_url': product.image.url if product.image else '',
                'personalized_text': personalized_text,
            })
        else:
            messages.error(request, f"Na voljo je samo še {available_stock} kosov.")
            return redirect('product_detail', pk=product_id)

    request.session['cart'] = cart

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        total_items = sum(item['quantity'] for item in cart) #Štejemo elemente v košarici
        return JsonResponse({'cart_count': total_items})

    return redirect('sentjur-merch')



@require_POST
def remove_from_cart(request):
        product_id = request.POST.get('product_id')
        selected_price_id = int(request.POST.get('selected_price_id'))
        selected_size_id = request.POST.get('selected_size_id')
        personalized_text = request.POST.get('personalized_text')

        cart = request.session.get('cart', [])

        updated_cart = []
        for item in cart:
            if (str(item['product_id']) == str(product_id)
                    and item['selected_price_id'] == selected_price_id
                    and item['selected_size_id'] == selected_size_id
                    and str(item['personalized_text']) == personalized_text):
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
    personalized_text = request.POST.get('personalized_text')


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
                if str(item['personalized_text']) == personalized_text:
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
    delivery_price = ProductPrice.objects.get(id=10).price
    total_price = 0
    for item in cart:
        item_price = float(item['price_item'])
        item_total = item_price * item['quantity']
        item['price_per_unit'] = item_price
        item['total_price'] = item_total
        total_price += item_total
    total_price_no_ddv = round(total_price/1.22,2)
    ddv = round(total_price-total_price/1.22,2)


    context = {
        'cart': cart,
        'ddv': ddv,
        'total_price_no_ddv': total_price_no_ddv,
        'total_price': total_price,
        'delivery_price': delivery_price,
        'total_price_with_delivery': float(total_price) + float(str(delivery_price)),

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
    checkout_data = request.session.get('checkout_data', {})

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            pass
        else:
            request.session['checkout_data'] = request.POST.dict()
    else:
        form = CheckoutForm(initial=checkout_data)

    return render(request, "shop/checkout.html", {
        "form": form,
        "cart": cart,
        "checkout_data": checkout_data
    })

@csrf_exempt  # ker ga kličeš preko JS fetch
def save_checkout_session(request):
    if request.method == "POST":
        request.session['checkout_data'] = request.POST.dict()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"}, status=400)


#Stripe plačila (paypal, revolut, applepay, googlepay, sepa, card itd...
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
                    html_message = render_to_string("shop/emails/payment_confirmation.html", {"order": order})
                    send_mail(
                        subject=f'Plačilo uspešno #{order.id}',
                        message="",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        html_message=html_message,  # točno ime parametra
                        fail_silently=True,
                    )

                print(f"✅ Naročilo {order_id} za {email} uspešno plačano (Elements).")
                stripe_logs_create(event['id'], event['type'], order, event, True)
                send_invoice_email(order)
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
    order_id = request.GET.get("order_id")

    if not order_id:
        messages.error(request, "Ni podatkov o naročilu.")
        return redirect("home")

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "Naročilo ne obstaja.")
        return redirect("home")

    # Ko pride sem, pomeni da je checkout šel čez.
    # Webhook pa bo v nekaj sekundah potrdil plačilo in poslal mail.
    if "cart" in request.session:
        del request.session["cart"]

    subject = f"Potrditev naročila #{order.id}"
    html_message = render_to_string("shop/emails/order_confirmation.html", {"order": order})
    send_mail(
        subject,
        "",  # plain-text verzija (pusti prazno ali dodaj)
        settings.DEFAULT_FROM_EMAIL,
        [order.email],  # predpostavljam, da ima order customer z email poljem
        html_message=html_message,
        fail_silently=False,
    )

    messages.success(
        request,
        "Naročilo je bilo uspešno oddano. Potrditev plačila boš prejel po e-pošti."
    )
    return redirect("home")

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
    phone = request.POST.get('phone', '')
    city = request.POST.get('city', '')
    postal_code = request.POST.get('postal_code', '')
    name = request.POST.get('name')
    surname = request.POST.get('surname')
    comment = request.POST.get('comment')
    company_check = request.POST.get('company') == 'on'
    newsletter_check = request.POST.get('newsletter') == 'on'
    company_name = request.POST.get('company_name')
    vat_number = request.POST.get('vat_number')
    company_address = request.POST.get('company_address')
    company_postal_code = request.POST.get('company_postal_code')
    company_city = request.POST.get('company_city')



    if not email or not address:
        return JsonResponse({'error': 'Vsa polja so obvezna.'}, status=400)

    cart = request.session.get('cart', [])
    if not cart:
        return JsonResponse({'error': 'Košarica je prazna.'}, status=400)

    user = request.user if request.user.is_authenticated else None

    total_amount = 0
    if True:  # GLS dostava, dokler ni drugih možnosti
        delivery_price = ProductPrice.objects.get(id=10)
        delivery_product = delivery_price.product  # če imaš FK do Product
        cart.append({
            'product_id': delivery_product.id,
            'product_name': delivery_product.name,
            'selected_price_id': delivery_price.id,
            'selected_size_id': None,
            'size_name': None,
            'price_item': str(delivery_price.price),
            'quantity': 1,
            'image_url': None,
            'personalized_text': None
        })
    for item in cart:
        price = ProductPrice.objects.get(id=item['selected_price_id'])
        total_amount += int(price.price * 100) * item['quantity']
    order = Order.objects.create(
        user=user,
        email=email,
        address=address,
        phone=phone,
        status=False,
        city=city,
        postal_code=postal_code,
        name=name,
        surname=surname,
        comment=comment,
        company_check=company_check,
        company_name=company_name,
        company_address=company_address,
        vat_number=vat_number,
        company_postal_code=company_postal_code,
        company_city=company_city,

    )

    obj, created = Newsletter.objects.get_or_create(email=email)

    if not obj.newsletter and newsletter_check:
        obj.newsletter = True
        obj.save()

    for item in cart:
        product = Product.objects.get(id=item['product_id'])
        price = ProductPrice.objects.get(id=item['selected_price_id'])
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item['quantity'],
            price=price, #price id
            price_at_order=price.price,
            price_tax=price.price_tax,
            personalized=item.get('personalized_text'),
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
        return JsonResponse({
            'client_secret': intent.client_secret,
            'order_id': order.id,
            'amount': total_amount,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def stripe_pay(request):
    client_secret = request.GET.get('client_secret')
    order_id = request.GET.get('order_id')
    amount = float(request.GET.get('amount', 0)) / 100
    return render(request, 'shop/stripe_pay.html', {
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'client_secret': client_secret,
        'order_id': order_id,
        'amount': amount,
    })


#Crypto plačila wihi
COINBASE_API_KEY = settings.COINBASE_API_KEY
client = Client(api_key=COINBASE_API_KEY)

def create_crypto_charge(order):
    try:
        charge = client.charge.create(
            name=f"Order #{order.id}",
            description="Plačilo z kriptovaluto",
            local_price={"amount": f"{order.get_total():.2f}", "currency": "EUR"},
            pricing_type="fixed_price",
            metadata={"order_id": str(order.id)},
            redirect_url= "https://5cec6f189adb.ngrok-free.app/success/", #"https://sentjur-metropola.si/success/",
            cancel_url="https://5cec6f189adb.ngrok-free.app/cancel/" #"https://sentjur-metropola.si/cancel/"
        )
        return charge.hosted_url

    except Exception as e:
        logging.exception("Coinbase charge creation failed")
        return None

def crypto_payment_redirect(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    hosted_url = create_crypto_charge(order)
    if hosted_url:
        return redirect(hosted_url)
    else:
        # fallback stran
        return redirect("/cancel/")

def coinbase_logs_create(event_id, event_type, order, event, payment_intent):
    CoinbaseLogs.objects.create(
        event_id=event_id,
        event_type=event_type,
        order_id=order,
        payload=json.dumps(event),
        processed_successfully=payment_intent
    )
@csrf_exempt
def coinbase_webhook(request):
    secret = settings.COINBASE_WEBHOOK_SECRET
    signature = request.META.get('HTTP_X_CC_WEBHOOK_SIGNATURE', '')
    payload = request.body

    computed_sig = hmac.new(
        key=bytes(secret, 'utf-8'),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_sig, signature):
        return HttpResponse("Invalid signature", status=400)

    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        return HttpResponse("Invalid JSON", status=400)

    # Shrani log
    order_id = event["event"]["data"]["metadata"].get("order_id")
    order = None
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            order = None

    coinbase_logs_create(event["id"], event["event"]["type"], order, event, False)

    # Posodobi order status
    metadata = event.get("event", {}).get("data", {}).get("metadata") or {}
    order_id = metadata.get("order_id")
    #TEST
    #order_id = 64

    if not order_id:
        return HttpResponse("Missing order_id", status=400)
    try:
        order = Order.objects.get(id=order_id)
        event_type = event["event"]["type"]

        if event_type == "charge:confirmed":
            order.status = True
            order.save()

    except Order.DoesNotExist:
        pass  # ali logiraj

    return HttpResponse("OK", status=200)

def export_invoice_csv(order):
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=';')
    writer.writerow([
        "#", "Šifra artikla", "Naziv artikla", "Kol.",
        #"EM", "Cena brez DDV", "MPC", "R %", "DDV %",
        #"Vrednost brez DDV", "Vrednost", "Opis artikla",
        #"Črtna koda",
    ])
    numerator = 0
    for item in order.items.all():
        numerator += 1
        writer.writerow([
            numerator,
            f"{item.price.id:06d}",
            item.product.name,
            item.quantity,
            #'kos',
            #f"{float(item.price_at_order) / 1.22:.2f}",
            #f"{item.price_at_order:.2f}",
            #'0',
            #'22',
            #f"{float(item.price_at_order) * float(item.quantity) / 1.22:.2f}",
            #f"{float(item.quantity) * float(item.price_at_order):.2f}",
            #f"Tekstil: {item.product.name}",
            #'00001',
        ])

    return buffer.getvalue()  # vrne vsebino CSV kot string

def send_invoice_email(order):
    csv_content = export_invoice_csv(order)

    subject = f"CSV datoteka za naročilo #{order.id}"
    if order.company_check:
        body = f"""Pošiljam naročilo za podjetje:
                NAZIV: {order.company_name}
                DAVČNA ŠT.: {order.vat_number}
                NASLOV: {order.company_address}
                POŠTA IN KRAJ: {order.company_postal_code}, {order.company_city}

                Hvala za vnos!
                
                PODATKI ZA DOSTAVO:
                {order.name} {order.surname}
                {order.address}
                {order.postal_code}, {order.city}
                """
    else:
        body = f"""
        Pošiljam naročilo za {order.name} {order.surname},
        
        Hvala za vnos!
        
        PODATKI ZA DOSTAVO:
                {order.name} {order.surname}
                {order.address}
                {order.postal_code}, {order.city}
        """
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email="upravitelj@sentjur-metropola.si",  # ali settings.DEFAULT_FROM_EMAIL
        to=["ziga.heric@gmail.com"],
    )

    # Dodamo CSV kot priponko
    email.attach(
        filename=f"order_{order.id}.csv",
        content=csv_content,
        mimetype="text/csv"
    )

    email.send(fail_silently=False)