from django.contrib import admin

from store.models import Order, Category, Customer, Product, Size, PriceTypes

admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Size)
admin.site.register(PriceTypes)
