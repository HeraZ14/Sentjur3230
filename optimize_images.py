import os
from django.conf import settings
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'spletka.settings')
application = get_wsgi_application()

from store.models import Product, ProductImage  # Zamenjaj 'store' z tvojo app

from PIL import Image


def optimize_images():
    optimized_count = 0
    skipped_count = 0

    # Base mape (relativno do MEDIA_ROOT)
    product_gallery_dir = os.path.join(settings.MEDIA_ROOT, 'uploads/product_gallery')
    product_dir = os.path.join(settings.MEDIA_ROOT, 'uploads/product')

    print(f"Base mape: Product gallery: {product_gallery_dir}, Product: {product_dir}")

    # Preveri, če mape obstajajo
    if not os.path.exists(product_gallery_dir):
        print(f"Mapa '{product_gallery_dir}' ne obstaja – upload-aj slike prej!")
        return
    if not os.path.exists(product_dir):
        print(f"Mapa '{product_dir}' ne obstaja.")

    # Loop za vse Product.image (glavne slike v 'uploads/product/')
    for product in Product.objects.all():
        if product.image:
            # Konstruiraj relativno pot: upload_to + filename
            filename = os.path.basename(product.image.name)  # Samo ime datoteke, npr. 'IMG_1687.jpg'
            img_path = os.path.join(product_dir, filename)
            if os.path.exists(img_path):
                try:
                    with Image.open(img_path) as img:
                        img.thumbnail((1200, 800), Image.Resampling.LANCZOS)
                        # Shrani kot WebP (prepiše)
                        img.save(img_path, 'WEBP', quality=85, optimize=True)
                        print(
                            f"Optimizirano (Product {product.id}): {img_path} (nova velikost: {os.path.getsize(img_path)} bytes)")
                        optimized_count += 1
                except Exception as e:
                    print(f"Napaka pri Product {product.id} ({img_path}): {e}")
            else:
                print(f"Preskočeno (ni datoteke): Product {product.id} - {img_path}")
                skipped_count += 1

    # Loop za vse ProductImage (v 'uploads/product_gallery/')
    for img_instance in ProductImage.objects.all():
        if img_instance.image:
            filename = os.path.basename(img_instance.image.name)
            img_path = os.path.join(product_gallery_dir, filename)
            if os.path.exists(img_path):
                try:
                    with Image.open(img_path) as img:
                        img.thumbnail((1200, 800), Image.Resampling.LANCZOS)
                        img.save(img_path, 'WEBP', quality=85, optimize=True)
                        print(
                            f"Optimizirano (ProductImage {img_instance.id}): {img_path} (nova velikost: {os.path.getsize(img_path)} bytes)")
                        optimized_count += 1
                except Exception as e:
                    print(f"Napaka pri ProductImage {img_instance.id} ({img_path}): {e}")
            else:
                print(f"Preskočeno (ni datoteke): ProductImage {img_instance.id} - {img_path}")
                skipped_count += 1

    print(f"Skupaj optimiziranih: {optimized_count}, preskočenih: {skipped_count}")


if __name__ == "__main__":
    optimize_images()