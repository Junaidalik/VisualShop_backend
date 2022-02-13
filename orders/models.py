from django.db import models
from django.core.validators import MinValueValidator, RegexValidator, MaxValueValidator
from customer.models import Customer, City
from shop.models import Product

# Create your models here.


class Cuopen(models.Model):
    minPurchase = models.DecimalField(
        decimal_places=3, max_digits=8, validators=[MinValueValidator(0)])
    expiryDate = models.DateField()
    totalQuantity = models.IntegerField(validators=[MinValueValidator(0)])
    discountPercentage = models.IntegerField(
        default=0, validators=[MinValueValidator(0)])
    cuopenCode = models.IntegerField(unique=True)

    def __str__(self):
        return f'{self.cuopenCode}: for purchase > {self.minPurchase} till: {self.expiryDate}'


class Order(models.Model):
    orderDate = models.DateField(auto_now_add=True)
    totalPrice = models.DecimalField(decimal_places=3, max_digits=8)
    shippingAddress = models.TextField()
    receiverName = models.CharField(max_length=50)
    receiverContact = models.CharField(max_length=11, validators=[RegexValidator(
        "^[0-9]{11}$", 'Contact number should consist of 11 digits')])
    orderStatus = models.CharField(max_length=50, default="PAYMENTPENDING", choices=(
        ("shipping", "SHIPPING"), 
        ("received", "RECEIVED"), 
        ("Payment pending", "PAYMENTPENDING"),
        ("canceled", "CANCELED")
    ))
    cuopenId = models.ForeignKey(
        Cuopen, on_delete=models.SET_NULL, null=True, blank=True)
    customerId = models.ForeignKey(Customer, on_delete=models.PROTECT)
    cityId = models.ForeignKey(City, on_delete=models.PROTECT)
    strip_client_id = models.CharField(max_length=500,blank=True,null=True)

    def __str__(self):
        return f'{self.receiverName} : {self.orderDate}'


class OrderedProduct(models.Model):
    totalQuantity = models.IntegerField(validators=[MinValueValidator(1)])
    totalPrice = models.DecimalField(decimal_places=3, max_digits=8)
    colourSelected = models.CharField(max_length=50,blank=True,null=True)
    sizeSelected = models.CharField(max_length=50,blank=True,null=True)
    productId = models.ForeignKey(Product, on_delete=models.PROTECT,related_name="orderedProducts")
    orderId = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="orderedProducts")

    def __str__(self):
        return f'orderId: {self.orderId}'


class Complaints(models.Model):
    orderId = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="complaints")
    complaintStatus = models.CharField(max_length=50, choices=(
        ("pending", "PENDING"), ("solved", "SOLVED")), default="pending")  # should use regular expression


class Messages(models.Model):
    complainId = models.ForeignKey(
        Complaints, on_delete=models.CASCADE, related_name="messages")
    message = models.TextField(max_length=1000)
    isAdmin = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        get_latest_by = ['date', 'id']

    def __str__(self):
        return self.message


class Feedback(models.Model):
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    description = models.TextField(max_length=500)
    orderedProductId = models.OneToOneField(
        OrderedProduct, on_delete=models.CASCADE,related_name="feedbacks")

    def __str__(self):
        return str(self.rating)
