
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Django Stock Trading API",
      default_version='v1',
      description="""
      `Stock Trading API`
      
      The Stock Trading API allows users to register, view stock data, and execute trades. Key <br>functionalities include:
      - User Registration: Register user with username and initial balance.
      - Tranactions: Users can initiate new transactions and review their transaction history..
      - Designed for a seamless trading experience!
      """,
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="sohailcs140@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path("", include('app.urls')),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
