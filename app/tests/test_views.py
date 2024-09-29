from app.models import (User, StockData, Transaction)
from django.db import IntegrityError
from uuid import UUID
from django.utils import timezone
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from django.core.cache import cache


class UserViewSetTests(APITestCase):
    """Test Cases For UserViewSet"""
    
    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'sohail',
            'balance': 1000
        }
        self.post_url = reverse('users-list')
        self.get_url = reverse('users-detail', kwargs={'username':self.user_data['username']})
    
    
    def test_create_user_with_valid_data(self):
        
        response = self.client.post(path=self.post_url, data=self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "User created")
        self.assertTrue(User.objects.filter(username=self.user_data['username']).exists())
    
    
    def test_create_user_with_missing_data(self):
        """Test creating a user with missing required fields"""
        
        data = self.user_data.copy()
        data.pop('username')
        
        response = self.client.post(path=self.post_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data) 
    
    
    
    def test_retrieve_user(self):
        """Test retrieving a user"""
        
        
        response = self.client.get(path=self.get_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user_data['username'])
    
    
    def test_retrieve_user_not_found(self):
        """Test retrieving a user that does not exist"""
        
        response = self.client.get(path=reverse('users-detail', kwargs={'username':'invalid user'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



class StockViewSetTests(APITestCase):
    """Test suite for StockViewSet."""
     
    def setUp(self):
        """Set up test data for StockViewSet tests."""
        self.stock_data = {
            'ticker': 'AAPL',
            'open_price':150,
            'close_price': 155,
            'high': 156,
            'low': 149,
            'volume': 1000000
        }
        self.create_url = reverse('stocks-list')  
        self.retrieve_url = reverse('stocks-detail', args=['AAPL'])  
    
    
    def test_create_stock(self):
        """Test creating a stock."""
        response = self.client.post(self.create_url, self.stock_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "stock created")
        self.assertTrue(StockData.objects.filter(ticker=self.stock_data['ticker']).exists())
        

    def test_create_stock_with_invalid_data(self):
        
        stock_data = self.stock_data
        stock_data.pop('ticker')
        response = self.client.post(self.create_url, self.stock_data)
        
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ticker', response.data)
    
    
    def test_retrieve_stock(self):
        """Test retrieving a stock"""
        StockData.objects.create(**self.stock_data)
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ticker'], self.stock_data['ticker'])
    
    
    def test_retrieve_stock_not_found(self):
        """Test retrieving a stock that does not exist"""
        response = self.client.get(path=reverse('stocks-detail', kwargs={'ticker':'invalid ticker'}))
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    
    def test_stock_list(self):
        
        response = self.client.get(path=self.create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class TransactionViewSetTestCases(APITestCase):
    """Test Cases For TransactionViewSet"""
    
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create(username='test_user', balance=1000)
        self.stock = StockData.objects.create(
            **{
            'ticker': 'AAPL',
            'open_price':150,
            'close_price': 155,
            'high': 156,
            'low': 149,
            'volume': 1000000
        }
        )
        self.transaction_data = {
            'user': self.user.pk,
            'ticker': 'AAPL',
            'transaction_type': 'buy',
            'transaction_volume': 5
        }
        self.create_url = reverse('create-transaction')
        self.user_transactions_url = reverse('user-transactions', args=[self.user.user_id])
        self.user_transactions_range_url = reverse('user-transactions_in_date_range', args=[
            self.user.user_id,
            timezone.now() - timezone.timedelta(days=30),
            timezone.now()
        ])


    def test_create_transaction(self):
        """Test creating a transaction when balance is sufficient"""
        
        response = self.client.post(path=self.create_url, data=self.transaction_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Transaction is in progress.')


    @patch('app.views.TransactionViewSet._is_balance_sufficent')
    def test_create_transacation_with_insufficient_balance(self, mock_is_balance_sufficent):
        """Test creating a transaction when balance is insufficient."""
        
        mock_is_balance_sufficent.return_value = False
        response = self.client.post(self.create_url, self.transaction_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Insufficient balance for this transaction.')
    
    
    def test_create_transaction_with_invalid_data(self):
        """Test creating a transaction with invalid data"""
        
        invalid_data = {
            'user': self.user.pk,
            'ticker': 'AAPL',
            'transaction_type': 'invalid_type',  
            'transaction_volume': 5
        }

        response = self.client.post(self.create_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('transaction_type', response.data)  
    
    
    def test_user_transactions(self):
        """Test retrieving all transactions for a specific user."""
        Transaction.objects.create(
            user=self.user,
            ticker='AAPL',
            transaction_type='buy',
            transaction_volume=5,
            transaction_price=55
        )

        response = self.client.get(self.user_transactions_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  
        self.assertEqual(response.data[0]['ticker'], 'AAPL')
        
    
    def test_get_user_transactions_within_range(self):
        """Test retrieving transactions of user within a specific date range"""
        Transaction.objects.create(
            user=self.user,
            ticker='AAPL',
            transaction_type='buy',
            transaction_volume=5,
            transaction_price=155,
            timestamp=timezone.now() - timezone.timedelta(days=15)
        )

        response = self.client.get(self.user_transactions_range_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    
