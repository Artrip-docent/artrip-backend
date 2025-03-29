from django.urls import path
from .views import chat_view, admin_page

urlpatterns = [
    path("", chat_view, name="chat"),
path('admin-page/', admin_page, name='admin_page'),
]