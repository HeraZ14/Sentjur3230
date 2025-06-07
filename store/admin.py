from django.contrib import admin

from store.models import Order, Category, Customer, Product, Size, ProductSize, PriceTypes


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 0  # število praznih vrstic za dodajanje

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductSizeInline]
    list_display = ['name']
    readonly_fields = ['total_stock']

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(Size)
admin.site.register(PriceTypes)

