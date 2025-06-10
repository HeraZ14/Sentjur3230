from django.db import models
from django.contrib.auth.models import User
from store.models import Product


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    address = models.TextField(max_length=100, default="", blank=True, null=True)
    phone = models.CharField(max_length=100, default="", blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
