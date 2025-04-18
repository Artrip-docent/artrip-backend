from django.urls import path
from .views import exhibition_list

urlpatterns = [
    path('', exhibition_list, name='exhibition-list'),
]
