from celery import shared_task
from .models import (Transaction, StockData, User)
from .utils import delete_from_cache
from django.db import transaction


@shared_task(name="process_transaction")
def process_transaction_async(validated_data):
    
    with transaction.atomic():
        
        user:User = User.objects.get(pk=validated_data['user'])
        stock_data:StockData = StockData.objects.get(ticker=validated_data['ticker'])
        transaction_type:str = validated_data['transaction_type']  
        transaction_volume:int = validated_data['transaction_volume']  


        if transaction_type == 'buy':
            user.balance -= stock_data.close_price * transaction_volume
            stock_data.volume -= transaction_volume
            
        if transaction_type == 'sell':
            user.balance += stock_data.close_price * transaction_volume
            stock_data.volume += transaction_volume
            
        user.save()
        stock_data.save()


        delete_from_cache(key=user.username)
        delete_from_cache(key=stock_data.ticker)
        delete_from_cache(key=f"{user.username}_transactions")
        delete_from_cache(key='stock_data')
        
        Transaction.objects.create(
            user=user,
            transaction_type=transaction_type,
            transaction_volume=transaction_volume,
            transaction_price=stock_data.close_price,
            ticker=validated_data['ticker'],
        )
    