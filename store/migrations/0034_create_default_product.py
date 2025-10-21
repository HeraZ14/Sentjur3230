from django.db import migrations, models
import os
import django.db.models.deletion
from store.models import generate_product_prices
import stripe


admin_password = os.getenv('DJANGO_ADMIN_PASSWORD', 'admin123')


def create_default_product(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Product = apps.get_model('store', 'Product')
    Category = apps.get_model('store', 'Category')
    PriceTypes = apps.get_model('store', 'PriceTypes')
    ProductPrice = apps.get_model('store', 'ProductPrice')  # Dodano: za konsistentnost

    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='ziga.heric@gmail.com',
            password=admin_password
        )

    category, _ = Category.objects.get_or_create(name="Settings")

    # Ustvari produkt
    product = Product.objects.create(
        name="Dostava",
        weight=3.17,
        category=category,
        description="Dostava.",
        settings=True
    )

    # Ostali del (PriceTypes get_or_create)
    price_type, _ = PriceTypes.objects.get_or_create(
        name="Settings",
        defaults={
            'price': 1,
            'settings': True,
            'description': ''
        }
    )

    try:
        settings_price_type = PriceTypes.objects.get(settings=True)
    except PriceTypes.DoesNotExist:
        return

    price = product.weight
    pp, created = ProductPrice.objects.update_or_create(
        product=product,
        price_type=settings_price_type,
        defaults={'price': price}
    )
    # Stripe sync
    if not pp.stripe_product_id:
        stripe_product = stripe.Product.create(name=product.name)
        pp.stripe_product_id = stripe_product.id
    if not pp.stripe_price_id:
        stripe_price = stripe.Price.create(
            product=pp.stripe_product_id,
            unit_amount=int(pp.price * 100),
            currency="eur"
        )
        pp.stripe_price_id = stripe_price.id
    pp.save()


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0033_alter_product_image'),  # popravi ime prejšnje migracije
    ]

    operations = [
        migrations.RunPython(create_default_product),
    ]