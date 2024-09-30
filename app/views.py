from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import F, Q
from .utils import (store_in_cache, get_from_cache, delete_from_cache)
from .serializers import (UserSerialzier, StockSerializer, TransactionSerializer)
from .models import (User, StockData)
from .tasks import process_transaction_async
from drf_yasg.utils import swagger_auto_schema

class UserViewSet(ViewSet):
    """
    ViewSet to handle user registration and retrieval.
    """
    lookup_field = "username"
    
    @swagger_auto_schema(request_body=UserSerialzier)
    def create(self, request):
        """
        Create a new user and store the user data in the cache.
        """
        serializer:UserSerialzier = UserSerialzier(data=request.data)
        
        
        if serializer.is_valid():
            user:User = serializer.save()
            store_in_cache(key=user.username, value=serializer.data)
            
            
            return Response({"message": "User created", "user_id": user.user_id}, status=status.HTTP_201_CREATED)


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def retrieve(self, request, username=None):
        """
        Retrieve user data by username. Check cache first, then database.
        """
        cache_user = get_from_cache(key=username)
        
        
        if cache_user:
            print("GET FORM CACHE")
            return Response(cache_user, status=status.HTTP_200_OK)
        
        
        user:User  = get_object_or_404(User, username=username)
        serializer:UserSerialzier = UserSerialzier(user)
        
        store_in_cache(key=user.username, value=serializer.data)
        print("GET FORM DATABASE")
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class SotckViewSet(ViewSet):
    """
    ViewSet to handle stock data operations, including creation, listing, and retrieval of stock records.
    """
    lookup_field:str = "ticker"
    
    @swagger_auto_schema(request_body=StockSerializer)
    def create(self, request:Request):
        """
        Create a new stock record and clear the stock cache.
        """
        serializer:StockSerializer = StockSerializer(data=request.data)
        
        
        if serializer.is_valid():
            serializer.save()
            delete_from_cache("stock_data")
            return Response(data={'message': "stock created", 'stock': serializer.data}, status=status.HTTP_201_CREATED)
        
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def list(self, request:Request):
        """
        List all stock records. First check the cache, then query the database if needed.
        """
        stock_data = get_from_cache(key='stock_data')
        
        if stock_data:
            print("get from cache")
            return Response(data=stock_data, status=status.HTTP_200_OK)
        
    
        stock_data = StockData.objects.all()
        serializer = StockSerializer(stock_data, many=True)
        
        
        if stock_data.exists():
            store_in_cache(key='stock_data', value=serializer.data, timeout=settings.CACHE_TIMEOUT_FOR_STOCK)
            
            
        print("get from database")
        return Response(serializer.data, status=status.HTTP_200_OK)        
        

    def retrieve(self, request:Request, ticker:str):
        """
        Retrieve a specific stock record by ticker. First check the cache, then the database.
        """
        stcok_data = get_from_cache(key=ticker)
        
        if stcok_data:
            print("GET FROM CACHE")
            return Response(data=stcok_data, status=status.HTTP_200_OK)
        
        stock_data = get_object_or_404(StockData, ticker=ticker)
        serializer = StockSerializer(stock_data)
        

        if stock_data:
            store_in_cache(key=ticker, value=serializer.data)
        print('GET FROM DATABAES')
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionViewSet(ViewSet):
    """
    ViewSet to handle transactions, including creation, listing, and retrieval of user transactions.
    """
    
    @swagger_auto_schema(request_body=TransactionSerializer)
    def create(self, request:Request)->Response:
        """
        Create a new transaction and pass the processing to a Celery task if the request is valid.
        """
        request_data = request.data.copy()
        if 'transaction_type' in request.data:
            request_data['transaction_type'] = request_data['transaction_type'].lower()
            
        serialzer:TransactionSerializer = TransactionSerializer(data=request_data)
        
        if serialzer.is_valid():
            if self._is_balance_sufficent(serialzer.validated_data):
                # pass process to celery
                process_transaction_async.delay(serialzer.data)
                
                return Response({'message':'Transaction is in progress.'}, status=status.HTTP_200_OK)
            return Response({'message':'Insufficient balance for this transaction.'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        return Response(serialzer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    @action(detail=False, methods=['get'], url_path='user-transactions')
    def user_transactions(self, request:Request, user_id:str):
        """
        Retrieve all transactions for a specific user.
        """
        user:User = get_object_or_404(User, user_id=user_id)
        
        cache_transactions = get_from_cache(key=f"{user.username}_transactions")
        if cache_transactions:
            print("GET TRANSACTIONS FROM CACHE")
            return Response(cache_transactions, status=status.HTTP_200_OK)
        
        transactions = user.transactions.all()
        serializer = TransactionSerializer(transactions, many=True)
        if len(transactions):
            store_in_cache(key=f"{user.username}_transactions", value=serializer.data)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    @action(detail=False, methods=['GET'])
    def get_user_transactions_within_range(self, reqeuest, user_id, start_timestamp, end_timestamp):
        """
        Retrieve all transactions for a specific user within a given timestamp range.
        """
        user:User = get_object_or_404(User, user_id=user_id)
        
        cache_transactions = get_from_cache(key=f"{user.username}_{start_timestamp}_{end_timestamp}_transactions")
        if cache_transactions:
            print("GET TRANSACTIONS FROM CACHE")
            return Response(cache_transactions, status=status.HTTP_200_OK)
        
        transactions = user.transactions.filter(timestamp__range=[start_timestamp, end_timestamp])
        serializer = TransactionSerializer(transactions, many=True)
        # store in cache
        if len(transactions):
            store_in_cache(key=f"{user.username}_{start_timestamp}_{end_timestamp}_transactions", value=serializer.data)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def _is_balance_sufficent(self, validated_data)->bool:
        """
        Check if the user's balance is sufficient for the transaction.
        """
        user:User = validated_data['user']
        stock_data:StockData = get_object_or_404(StockData, ticker=validated_data['ticker'])
        transaction_type:str = validated_data['transaction_type']
        transaction_volume:int = validated_data['transaction_volume']
        
        
        return not (transaction_type == 'buy' and user.balance < stock_data.close_price * transaction_volume)