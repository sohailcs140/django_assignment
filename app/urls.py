from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, SotckViewSet, TransactionViewSet


router = DefaultRouter()
router.register("users", viewset=UserViewSet, basename="users")
router.register("stocks", viewset=SotckViewSet, basename="stocks")


transaction_urls  = [
    path('transactions/', TransactionViewSet.as_view({'post':'create'}), name='create-transaction'),
    path('transactions/<str:user_id>/', TransactionViewSet.as_view({'get': 'user_transactions'}), name="user-transactions"),
    path('transactions/<str:user_id>/<str:start_timestamp>/<str:end_timestamp>/', TransactionViewSet.as_view({'get': 'get_user_transactions_within_range'}), name="user-transactions_in_date_range")
]


urlpatterns = [
    path("", include(router.urls)),
    path("", include(transaction_urls))
]   
