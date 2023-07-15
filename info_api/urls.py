from django.urls import path, include
from .views import (
    InfoAPI,
    DownloadAPI
)

urlpatterns = [
    path('', InfoAPI.as_view()),
    path('download', DownloadAPI.as_view())
]