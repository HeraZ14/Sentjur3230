from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms
import stripe
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit

# Create your models here.

#Kategorije produktov
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

#Produkti
class Product(models.Model):
    name = models.CharField(max_length=100)
    weight = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE,default=1)
    description = models.TextField(default="", blank=True,null=True)
    composition = models.TextField(default="", blank=True,null=True)
    return_items = models.TextField(default="", blank=True,null=True)
    image = ProcessedImageField(  # <-- Spremeni iz ImageField
        upload_to='uploads/product/',  # Ohrani isto mapo
        processors=[ResizeToFit(1600, 1600)],  # Max 1600x1600, proporcionalno (ohranja razmerja!)
        format='WEBP',
        options={'quality': 90},
        blank=True,
        null=True,
        verbose_name='Slika'
    )
    personalized = models.BooleanField(default=False)
    settings = models.BooleanField(default=False)
    def total_stock(self):
        print(f"Product: {self.name}, Sizes: {[ps.quantity for ps in self.product_sizes.all()]}")
        return sum(ps.quantity for ps in self.product_sizes.all())
    total_stock.short_description = 'Total Stock'
    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = ProcessedImageField(  # <-- Spremeni iz ImageField
        upload_to='uploads/product_gallery/',
        processors=[ResizeToFit(1600, 1600)],  # <-- Max 1600x1600, proporcionalno skaliranje (ohranja razmerja!)
        format='WEBP',
        options={'quality': 90},
        verbose_name='Slika'
    )

    def __str__(self):
        return f"{self.product.name} - {self.id}"

class PriceTypes(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default="", blank=True,null=True, max_length=100)
    price = models.FloatField()
    is_main = models.BooleanField(default=False)
    settings = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class ProductPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price_type = models.ForeignKey(PriceTypes, on_delete=models.CASCADE)
    price = models.FloatField()
    is_main = models.BooleanField(default=False)
    stripe_product_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('product', 'price_type')

    def __str__(self):
        return f"{self.product.name} – {self.price_type.name}: {self.price} €"

    @property
    def price_tax(self):
        return round(self.price - self.price*1.22,2)

@receiver(post_save, sender=Product)
def generate_product_prices(sender, instance, **kwargs):
    if getattr(instance, 'settings', False):
        try:
            settings_price_type = PriceTypes.objects.get(settings=True)
        except PriceTypes.DoesNotExist:
            return

        price = round(instance.weight * 1.22,2)
        pp, created = ProductPrice.objects.update_or_create(
            product=instance,
            price_type=settings_price_type,
            defaults={'price': price, 'is_main': True}
        )
        # Stripe sync
        if not pp.stripe_product_id:
            stripe_product = stripe.Product.create(name=instance.name)
            pp.stripe_product_id = stripe_product.id
        if not pp.stripe_price_id:
            stripe_price = stripe.Price.create(
                product=pp.stripe_product_id,
                unit_amount=int(pp.price * 100),
                currency="eur"
            )
            pp.stripe_price_id = stripe_price.id
        pp.save()
    else:
        for pt in PriceTypes.objects.filter(settings=False):
            main = False
            if pt.is_main:
                main = True
            price = round(instance.weight * pt.price * 1.22, 2)
            pp, created = ProductPrice.objects.update_or_create(
                product=instance,
                price_type=pt,
                defaults={'price': price, 'is_main': main}
            )
            # Stripe sync
            if not pp.stripe_product_id:
                stripe_product = stripe.Product.create(name=instance.name)
                pp.stripe_product_id = stripe_product.id
            if not pp.stripe_price_id:
                stripe_price = stripe.Price.create(
                    product=pp.stripe_product_id,
                    unit_amount=int(pp.price * 100),
                    currency="eur"
                )
                pp.stripe_price_id = stripe_price.id

            pp.save()


class Size(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_sizes')
    size = models.ForeignKey(Size, on_delete=models.CASCADE, default=1)
    quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ('product', 'size')

    def __str__(self):
        return f"{self.product.name} - {self.size.name} ({self.quantity})"

class Cart(models.Model):
    session_key = models.CharField(max_length=100, default="")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart )"#({Customer.username})"

class CartItem(models.Model):
    session_key = models.CharField(max_length=100, blank=True, null=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="", blank=True, null=True)
    surname = models.CharField(max_length=100, default="", blank=True, null=True)
    address = models.TextField(max_length=100, default="", blank=True, null=True)
    city = models.TextField(max_length=100, default="", blank=True, null=True)
    postal_code = models.TextField(max_length=100, default="", blank=True, null=True)
    phone = models.CharField(max_length=100, default="", blank=True, null=True)
    email = models.EmailField(max_length=100, default="", blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=100, default="", blank=True, null=True)
    company_check = models.BooleanField(default=False)
    company_name = models.CharField(max_length=50,default="", blank=True, null=True)
    vat_number = models.CharField(max_length=50,default="", blank=True, null=True)
    company_address = models.CharField(max_length=200,default="", blank=True, null=True)
    company_postal_code = models.TextField(max_length=10,default="", blank=True, null=True)
    company_city = models.CharField(max_length=50,default="", blank=True, null=True)
    comment = models.TextField(default="", blank=True, null=True)

    def __str__(self):
        return str(self.user) if self.user else "Anonimen"

    def get_total(self):
        return sum(item.price_at_order * item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.price_at_order * item.quantity for item in self.items.all())

    def get_total_without_tax(self):
        return sum((item.price_at_order - item.price_tax) * item.quantity for item in self.items.all())

    @property
    def tax_amount(self):
        return sum(item.price_tax * item.quantity for item in self.items.all())

    @property
    def total_price_without_tax(self):
        return self.get_total_without_tax()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(ProductSize, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.ForeignKey(ProductPrice, on_delete=models.CASCADE,null=True, blank=True)
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    personalized = models.TextField(max_length=100, default="", blank=True, null=True)

class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    address = forms.CharField(max_length=200, required=True)
    postal_code = forms.CharField(max_length=10, required=True)
    city = forms.CharField(max_length=50, required=True)
    phone = forms.CharField(max_length=20, required=True)
    company_name = forms.CharField(max_length=50, required=True)
    vat_number = forms.CharField(max_length=50, required=True)
    company_address = forms.CharField(max_length=200, required=True)
    company_postal_code = forms.CharField(max_length=10, required=True)
    company_city = forms.CharField(max_length=50, required=True)

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    newsletter = models.BooleanField(default=False)

class StripeLogs(models.Model):
    event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=100)
    order_id = models.ForeignKey('Order', null=True, blank=True, on_delete=models.CASCADE, related_name='stripe_logs')
    received_at = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField(null=True, blank=True)
    processed_successfully = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.event_type} | Order #{self.order_id} | {self.event_id}"

class CoinbaseLogs(models.Model):
    event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=100)
    order_id = models.ForeignKey('Order', null=True, blank=True, on_delete=models.CASCADE, related_name='coinbase_logs')
    received_at = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField(null=True, blank=True)
    processed_successfully = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"{self.event_type} | Order #{self.order_id} | {self.event_id}"
