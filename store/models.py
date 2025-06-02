from django.db import models
import datetime
# Create your models here.

#Kategorije produktov
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

#Stranke
class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=100)

#Produkti
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE,default=1)
    description = models.TextField(default="", blank=True,null=True)
    image = models.ImageField(upload_to='uploads/product/')
    stock = models.IntegerField(default=0)
    def __str__(self):
        return self.name

#Naročila strank
class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    address = models.TextField(max_length=100, default="", blank=True,null=True)
    phone = models.CharField(max_length=100,default="",blank=True,null=True)
    date = models.DateTimeField(default=datetime.datetime.now)
    status = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.customer} - {self.product}"

class Cart(models.Model):
    user = models.OneToOneField(Customer, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart ({self.customer.username})"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def total_price(self):
        return self.product.price * self.quantity
