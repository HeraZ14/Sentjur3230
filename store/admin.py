from django.contrib import admin

from store.models import Category, Product, Size, ProductSize, PriceTypes, ProductPrice


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 0  # število praznih vrstic za dodajanje

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductSizeInline]
    list_display = ['name']
    readonly_fields = ['total_stock']

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Size)
admin.site.register(PriceTypes)
admin.site.register(ProductPrice)

