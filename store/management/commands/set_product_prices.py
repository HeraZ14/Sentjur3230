from django.core.management.base import BaseCommand
from store.models import Product, PriceTypes, ProductPrice

class Command(BaseCommand):
    help = "Generate all ProductPrices"

    def handle(self, *args, **kwargs):
        price_types = PriceTypes.objects.all()
        for product in Product.objects.all():
            for pt in price_types:
                price = round(product.weight * pt.price, 2)
                ProductPrice.objects.update_or_create(
                    product=product,
                    price_type=pt,
                    defaults={'price': price}
                )
        self.stdout.write(self.style.SUCCESS('All prices generated successfully.'))