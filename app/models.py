from django.db import models
from uuid import uuid4
from django.core.validators import MinValueValidator

TRANSACTION_TYPE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]


class User(models.Model):
    user_id = models.CharField(primary_key=True,max_length=36, default=uuid4)
    username = models.CharField(max_length=50, unique=True,blank=False, null=False)
    balance = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.0)])

    
    def __str__(self):
    
        return self.username




class StockData(models.Model):
    
    ticker = models.CharField(max_length=15, unique=True)
    open_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.0)])
    close_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.0)])
    high = models.DecimalField(max_digits=12, decimal_places=2)
    low = models.DecimalField(max_digits=12, decimal_places=2,validators=[MinValueValidator(0.0)])
    volume = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    
    
    def __str__(self)-> str:
        return self.ticker
    
    
    class Meta:
        ordering = ["-timestamp"]



class Transaction(models.Model):
    

    transaction_id = models.CharField(primary_key=True, max_length=36, default=uuid4)
    user = models.ForeignKey(to="User", on_delete=models.CASCADE, related_name="transactions")
    ticker = models.CharField(max_length=15)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPE_CHOICES)
    transaction_volume = models.IntegerField(validators=[MinValueValidator(1)])
    transaction_price = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        
        ordering = ["-timestamp"]
    
    
    

    
    
    

