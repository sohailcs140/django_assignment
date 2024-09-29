from rest_framework import serializers
from .models import (User, StockData, Transaction)
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404


class UserSerialzier(serializers.ModelSerializer):
    
    
    class Meta:
        model = User
        fields = ('username', 'balance', 'user_id')
        read_only_fields = ['user_id']

    
    def validate_username(self, value:str):
        
        if value.isdigit():
            raise ValidationError( 'The username must contain only alphabetic characters or a combination of letters, numbers, and special characters.')
        
        if value.__len__() < 3:
            raise ValidationError('The username must be at least 3 characters long.')
        
        return value

    
    
    
    
class StockSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = StockData
        fields = '__all__'


    def validate(self, attrs):
        validated_data = super().validate(attrs)
        low, high, open_price, close_price = validated_data['low'],validated_data['high'],validated_data['open_price'],validated_data['close_price']

        if low > high:
            raise ValidationError({
                'low': 'The low value must be less than or equal to the high value.'
            })
        
        if open_price > high:
            raise ValidationError({
                'open_price': 'The open price value must be less than or equal to the high value.'
            })
        
        
        if close_price > high:
            raise ValidationError({
                'close_price': 'The close price value must be less than or equal to the high value.'
            })
        
        
        if close_price < low:
            raise ValidationError({
                'close_price': 'The close price value must be greater than or equal to the low value.'
            })
        
        if open_price < low:
            raise ValidationError({
                'open_price': 'The open price value must be greater than or equal to the low value.'
            })
        
        return validated_data
    
    

class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['transaction_price', 'transaction_id', 'timestamp']
    
    
    def validate(self, attrs):
        
        validated_data = super().validate(attrs)
        stock_instance:StockData = get_object_or_404(StockData, ticker=validated_data['ticker'])


        if validated_data['transaction_type'] == 'buy' and (validated_data['transaction_volume'] > stock_instance.volume):
            
            raise ValidationError({
                'transaction_volume':'transaction_volume must be less than or equal to the stock volume'
            })
            
        
        
        return validated_data

   
    


    
    
