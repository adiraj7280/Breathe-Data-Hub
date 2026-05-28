from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NormalizedDataRecordViewSet, UploadDataView, InitialDataSetupView, ClearDatabaseView

router = DefaultRouter()
router.register(r'records', NormalizedDataRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', UploadDataView.as_view(), name='upload_data'),
    path('setup/', InitialDataSetupView.as_view(), name='initial_setup'),
    path('clear/', ClearDatabaseView.as_view(), name='clear_data'),
]
