from django.urls import path
from .views import ProtocolRequestView, ProtocolResultView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('request/', ProtocolRequestView.as_view(), name='protocol_request'),
    path('result/<uuid:job_id>/', ProtocolResultView.as_view(), name='protocol_result'),
    
    # OpenAPI Schema
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
