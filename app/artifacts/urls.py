"""
URL mappings for the artifacts app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from artifacts import views

app_name = 'artifacts'

router = DefaultRouter()
router.register(app_name, views.ArtifactsViewSet,
                basename=app_name)

urlpatterns = [
    path('', include(router.urls))
]
