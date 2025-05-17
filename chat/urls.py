from django.urls import path
from . import views

urlpatterns = [
path("", views.chat_view, name="chat"),
path('admin-page/', views.admin_page, name='admin_page'),
path("delete_document/<int:doc_id>/", views.delete_document, name="delete_document"),
path("history/", views.get_chat_history),
]