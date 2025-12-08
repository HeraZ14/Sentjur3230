import stripe
from django.conf import settings
from django.core.management.base import BaseCommand
from store.models import ProductPrice

stripe.api_key = settings.STRIPE_SECRET_KEY

class Command(BaseCommand):
    help = 'Sinhronizira produkte in cene s Stripe'

    def handle(self, *args, **options):
        for pp in ProductPrice.objects.all():
            pp.stripe_product_id = ""
            pp.stripe_price_id = ""
            pp.save()
        for pp in ProductPrice.objects.all():
            print(pp)
            if not pp.stripe_product_id:
                stripe_product = stripe.Product.create(name=pp.product.name)
                pp.stripe_product_id = stripe_product.id

            if not pp.stripe_price_id:
                stripe_price = stripe.Price.create(
                    product=pp.stripe_product_id,
                    unit_amount=int(pp.price * 100),
                    currency="eur"
                )
                pp.stripe_price_id = stripe_price.id


            pp.save()

        self.stdout.write("Vsi produkti in cene so sinhronizirani s Stripe.")
