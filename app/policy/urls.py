"""URL mappings for policy app"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from policy import views

app_name = 'policy'

router = DefaultRouter()
router.register(app_name, views.PolicyViewSet, basename=app_name)

urlpatterns = [
    path('', include(router.urls))
]
