import os
from django.conf import settings
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'spletka.settings')  # Zamenjaj 'your_project' z imenom tvojega projekta
application = get_wsgi_application()

from store.models import Product, ProductImage  # Zamenjaj 'store' z tvojo app (import obeh modelov)

from PIL import Image


def optimize_images():
    optimized_count = 0

    # Loop za vse Product.image (glavne slike)
    for product in Product.objects.all():
        if product.image:
            img_path = product.image.path
            try:
                with Image.open(img_path) as img:
                    # Ohrani razmerja: Skaliraj proporcionalno
                    img.thumbnail((1200, 800), Image.Resampling.LANCZOS)
                    # Shrani kot WebP (prepiše original)
                    img.save(img_path, 'WEBP', quality=85, optimize=True)
                    print(f"Optimizirano (Product): {img_path} (nova velikost: ~{os.path.getsize(img_path)} bytes)")
                    optimized_count += 1
            except Exception as e:
                print(f"Napaka pri Product {product.id} ({img_path}): {e}")

    # Loop za vse ProductImage (dodatne slike)
    for img_instance in ProductImage.objects.all():
        if img_instance.image:
            img_path = img_instance.image.path
            try:
                with Image.open(img_path) as img:
                    # Ohrani razmerja: Skaliraj proporcionalno
                    img.thumbnail((1200, 800), Image.Resampling.LANCZOS)
                    # Shrani kot WebP
                    img.save(img_path, 'WEBP', quality=85, optimize=True)
                    print(
                        f"Optimizirano (ProductImage): {img_path} (nova velikost: ~{os.path.getsize(img_path)} bytes)")
                    optimized_count += 1
            except Exception as e:
                print(f"Napaka pri ProductImage {img_instance.id} ({img_path}): {e}")

    print(f"Skupaj optimiziranih slik: {optimized_count}")


if __name__ == "__main__":
    optimize_images()