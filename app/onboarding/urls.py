"""
URL mappings for the Onboarding app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from onboarding import views

app_name = 'onboarding'

router = DefaultRouter()
router.register(app_name, views.OnboardingViewSet,
                basename=app_name)
router.register(r'onboarding-step', views.OnboardingStepViewSet,
                basename='onboarding-step')
urlpatterns = [
    path('', include(router.urls))
]
