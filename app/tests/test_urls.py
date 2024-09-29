from rest_framework.test import APITestCase
from django.urls import reverse
from app.models import (User, StockData)
from rest_framework import status
from decimal import Decimal

class UserUrlsTestCases(APITestCase):
    """Test User Urls"""
    
    def setUp(self) :
        self.user = User.objects.create(username="test_user", balance=7000)
    
    
    def test_user_list_url(self):
        
        response = self.client.get(path=reverse('users-list'))
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    
    def test_get_user_url(self):
        
        response = self.client.get(reverse('users-detail', kwargs={'username':self.user.username}))
        self.assertEqual(status.HTTP_200_OK, response.status_code)



class StockDataUrlsTestCases(APITestCase):
    
    def setUp(self):
        
        self.stock_data = {
            'ticker': 'AAPL',
            'open_price': Decimal('150.00'),
            'close_price': Decimal('155.50'),
            'high': Decimal('160.00'),
            'low': Decimal('149.50'),
            'volume': 1000000,
        }

        
        self.stock_instance = StockData.objects.create(**self.stock_data)
         
    
    
    def test_stock_list_url(self):
        
        response = self.client.get(reverse('stocks-list'))
        
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    
    def test_get_stock_url(self):
        
        response = self.client.get(reverse('stocks-detail', kwargs={'ticker':self.stock_instance.ticker}))
        self.assertEqual(status.HTTP_200_OK, response.status_code)