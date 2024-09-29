from rest_framework.test import APITestCase
from app.serializers import (UserSerialzier, StockSerializer, TransactionSerializer)
from app.models import (User, StockData, Transaction)
from decimal import Decimal


class UserSerializerTestCases(APITestCase):
    """Test cases for UserSerializer"""
    
    
    def setUp(self) -> None:
        """Set up test data for UserSerializer tests"""
        
        self.user_data = {
            'username': 'testuser',
            'balance': 500
        }

        self.user_instance = User.objects.create(**self.user_data)
    
    
    def test_user_serializer_valid_data(self):
        """Test that valid data passes validation and creates a User instance"""
        serializer = UserSerialzier(data={**self.user_data, 'username':'otheruser'})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['username'], 'otheruser')
        self.assertEqual(serializer.validated_data['balance'], self.user_data['balance'])

        
        user = serializer.save()
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, 'otheruser')
        self.assertEqual(user.balance, self.user_data['balance'])
    
    
    def test_user_serializer_invalid_data(self):
        """Test that invalid data fails validation"""
        invalid_data = self.user_data.copy()
        invalid_data['balance'] = 'invalid_balance'  

        serializer = UserSerialzier(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('balance', serializer.errors)
    
    
    def test_user_serializer_missing_required_field(self):
        """Test that missing required fields raise a validation error"""
        incomplete_data = self.user_data.copy()
        incomplete_data.pop('username')  

        serializer = UserSerialzier(data=incomplete_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        
    
    def test_user_serializer_read_only_field(self):
        """Test that read-only field user_id is not accepted in input"""
        data_with_user_id = self.user_data.copy()
        data_with_user_id['user_id'] = 999  
        data_with_user_id['username'] = 'user_with_read_only_field'
        serializer = UserSerialzier(data=data_with_user_id)
        self.assertTrue(serializer.is_valid())  
        self.assertNotIn('user_id', serializer.validated_data) 


    def test_user_serializer_serialization(self):
        """Test that the serializer correctly serializes a User instance"""
        serializer = UserSerialzier(self.user_instance)
        data = serializer.data
        
        self.assertEqual(data['username'], self.user_data['username'])
        self.assertEqual(data['balance'], '500.00')
        self.assertEqual(data['user_id'], str(self.user_instance.user_id))
        

class StockSearializerTestCases(APITestCase):
    """Test Cases for the StockSerializer"""
    
    
    def setUp(self):
        """Set up test data for StockSerializer"""
        self.stock_data = {
            'ticker': 'AAPL',
            'open_price': Decimal('150.00'),
            'close_price': Decimal('155.50'),
            'high': Decimal('160.00'),
            'low': Decimal('149.50'),
            'volume': 1000000,
        }

        
        self.stock_instance = StockData.objects.create(**self.stock_data)
    

    def test_stock_serializer_valid_data(self):
        """Test that valid data passes validation and creates a StockData instance"""
        serializer = StockSerializer(data={**self.stock_data, 'ticker':'MSFT'})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['ticker'], 'MSFT')
        self.assertEqual(serializer.validated_data['volume'], self.stock_data['volume'])

        stock = serializer.save()
        self.assertIsInstance(stock, StockData)
        self.assertEqual(stock.ticker, 'MSFT')
        self.assertEqual(stock.open_price, self.stock_data['open_price'])
    
    
    def test_stock_serializer_invalid_data(self):
        """Test that invalid data fails validation."""
        invalid_data = self.stock_data.copy()
        invalid_data['open_price'] = 'invalid_price' 

        serializer = StockSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('open_price', serializer.errors)

    
    def test_stock_serializer_missing_required_field(self):
        """Test that missing required fields raise a validation error"""
        incomplete_data = self.stock_data.copy()
        incomplete_data.pop('ticker')  

        serializer = StockSerializer(data=incomplete_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('ticker', serializer.errors)


    def test_stock_serializer_read_only_timestamp(self):
        """Test that timestamp is automatically handled and cannot be set in input"""
        data_with_timestamp = self.stock_data.copy()
        data_with_timestamp['timestamp'] = '2023-09-01T10:00:00Z'
        data_with_timestamp['ticker'] = 'GOOGL'
        serializer = StockSerializer(data=data_with_timestamp)
        self.assertTrue(serializer.is_valid())  
        self.assertNotIn('timestamp', serializer.validated_data) 


class TransactionSerializerTestCases(APITestCase):
    """Test Cases for  TransactionSerializer."""
    
    def setUp(self):
        """Set up test data for TransactionSerializer tests"""
        self.user = User.objects.create(username='transaction_user', balance=1000)
        
        self.stock = StockData.objects.create(
            ticker="AAPL",low=90,high=240, open_price=110, close_price=250,
            volume=120
            
        )
        self.transaction_data = {
            'user': self.user.user_id,
            'ticker': 'AAPL',
            'transaction_type': 'buy',
            'transaction_volume': 10,
        }

        self.transaction_instance = Transaction.objects.create(
            user=self.user,
            ticker='AAPL',
            transaction_type='buy',
            transaction_volume=10,
            transaction_price=Decimal('1500.00')
        )
        
    
    def test_transaction_serializer_valid_data(self):
        """Test that valid data passes validation and creates a Transaction"""
        serializer = TransactionSerializer(data=self.transaction_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['ticker'], self.transaction_data['ticker'])
        self.assertEqual(serializer.validated_data['transaction_volume'], self.transaction_data['transaction_volume'])
        serializer.validated_data['transaction_price'] = 40
        transaction = serializer.save()
        transaction.save()
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.ticker, self.transaction_data['ticker'])
        self.assertEqual(transaction.transaction_volume, self.transaction_data['transaction_volume'])


    def test_transaction_serializer_invalid_data(self):
        """Test that invalid data fails validation"""
        invalid_data = self.transaction_data.copy()
        invalid_data['transaction_volume'] = 'invalid value'

        serializer = TransactionSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('transaction_volume', serializer.errors)
    
    
    def test_transaction_serializer_missing_required_field(self):
        """Test that missing required fields fails validation"""
        transaction_data = self.transaction_data.copy()
        transaction_data.pop('ticker')  

        serializer = TransactionSerializer(data=transaction_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('ticker', serializer.errors)