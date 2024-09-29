from app.models import (User, StockData, Transaction)
from django.test import TestCase 
from django.db import IntegrityError
from uuid import UUID
from django.utils import timezone

class UserModelTestCases(TestCase):
    """Test Cases for the User model"""
    
    def setUp(self):
        """Set up initial user data for testing"""
        self.user_data = {'username':'rayan', 'balance':90}
        self.user = User.objects.create(**self.user_data)
    
    def test_user_creation(self):
        """Test the creation of a new user"""
        self.assertEqual(self.user.username, self.user_data.get('username'))
        self.assertEqual(self.user.balance, self.user_data['balance'])
    
    
    def test_update_user(self):
        """Test updating user fields"""
        self.user.username = "updated username"
        self.user.balance = 901
        self.user.save()
        
        self.assertEqual(self.user.username, "updated username")
        self.assertEqual(self.user.balance, 901)
    
    
    def test_delete_user(self):
        """Test deleting a user from the database"""
        self.user.delete()
        self.assertFalse(User.objects.exists())
    
    
    def test_user_creation_with_missing_data(self):
        """Test user creation raises IntegrityError when required fields are missing."""        
        missing_data =  {'username':'test_user'}
        
        
        with self.assertRaises(IntegrityError):
            User.objects.create(**missing_data)



class StockDataModelTestCases(TestCase):
    
    def setUp(self) -> None:
        self.stock_data = {
    "ticker":"AAPL",
    "open_price": 150,
    "close_price": 200,
    "high":250,
    "low":130,
     "volume":8900
}
        
        self.stock = StockData.objects.create(**self.stock_data)
    
    
    
    def test_stock_data_creation(self):
        
        self.assertEqual(self.stock.ticker, self.stock_data['ticker'])
        self.assertEqual(self.stock.open_price, self.stock_data['open_price'])
        self.assertEqual(self.stock.close_price, self.stock_data['close_price'])
        self.assertEqual(self.stock.high, self.stock_data['high'])
        self.assertEqual(self.stock.low, self.stock_data['low'])
        self.assertEqual(self.stock.volume, self.stock_data['volume'])
    
    
    
    def test_stock_data_update(self):
        
        updated_data = {
            "ticker":"AAPL",
            "open_price": 500,
            "close_price": 650,
            "high":670,
            "low":450,
            "volume":200
        }
        
        self.stock.ticker = updated_data['ticker']
        self.stock.open_price = updated_data['open_price']
        self.stock.close_price = updated_data['close_price']
        self.stock.volume = updated_data['volume']
        
        self.stock.save()
        
        self.assertEqual(self.stock.ticker, updated_data['ticker'])
        self.assertEqual(self.stock.open_price, updated_data['open_price'])
        self.assertEqual(self.stock.close_price, updated_data['close_price'])
        self.assertEqual(self.stock.volume, updated_data['volume'])
        
        self.assertTrue(StockData.objects.count() == 1)
    
    
    
    def test_stock_data_delete(self):
        
        id = self.stock.id
        
        self.stock.delete()
        
        with self.assertRaises(StockData.DoesNotExist):
            StockData.objects.get(id=id)
    


class TransactionModelTestCases(TestCase):
    """Test cases for Transaction model"""
    
    def setUp(self):
        """Set up initial data for testing."""
        
        self.user = User.objects.create(username='testuser', balance=1000)

        
        self.transaction_data = {
            'user': self.user,
            'ticker': 'AAPL',
            'transaction_type': 'buy',
            'transaction_volume': 10,
            'transaction_price': 150.00
        }


    
    def test_transaction_creation(self):
        """Test creating a new transaction."""
        transaction = Transaction.objects.create(**self.transaction_data)

        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.ticker, self.transaction_data['ticker'])
        self.assertEqual(transaction.transaction_type, self.transaction_data['transaction_type'])
        self.assertEqual(transaction.transaction_volume, self.transaction_data['transaction_volume'])
        self.assertEqual(transaction.transaction_price, self.transaction_data['transaction_price'])
        self.assertIsInstance(transaction.transaction_id, UUID)
        self.assertLessEqual(transaction.timestamp, timezone.now())  

    
    def test_transaction_foreign_key_user(self):
        """Test that deleting a user cascades to delete related transactions."""
        transaction = Transaction.objects.create(**self.transaction_data)
        
        
        self.assertTrue(Transaction.objects.filter(pk=transaction.transaction_id).exists())

        self.user.delete()
        self.assertFalse(Transaction.objects.filter(pk=transaction.transaction_id).exists())
