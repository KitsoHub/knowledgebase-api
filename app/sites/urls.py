from django.urls import path, include
from rest_framework.routers import DefaultRouter
from sites import views

app_name = 'sites'

router = DefaultRouter()
router.register(app_name, views.HeritageSiteViewSet, basename=app_name)
router.register('verification-votes',
                views.VerificationVoteViewSet, basename='verification-votes')

urlpatterns = [
    path('', include(router.urls))
]
