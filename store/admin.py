from django.contrib import admin

from store.models import Category, Product, Size, ProductSize, PriceTypes, ProductPrice, ProductImage, Order


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 0  # število praznih vrstic za dodajanje

class ProductImageInline(admin.TabularInline):  # ali StackedInline
    model = ProductImage
    extra = 1   # kolikokrat se prikaže prazen obrazec za dodajanje


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductSizeInline]
    list_display = ['name']
    readonly_fields = ['total_stock']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email', 'status', 'payment_method', 'date')
    list_filter = ('status', 'payment_method', 'date')
    search_fields = ('id', 'email', 'user')
    ordering = ('-date',)




admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Size)
admin.site.register(PriceTypes)
admin.site.register(ProductPrice)

