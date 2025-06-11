"""
URL configuration for Artrip project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

# 루트 URL에 간단한 메시지 반환
def home(request):
    return HttpResponse("Welcome to the Artrip project!")

# Swagger 설정
schema_view = get_schema_view(
    openapi.Info(
        title="Chat API",
        default_version="v1",
        description="Django Chat API with OpenAI GPT",
        terms_of_service="https://www.google.com/policies/terms/",
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

from django.urls import path, include

urlpatterns = [
    path('', home),  # 루트 URL 처리
    path("admin/", admin.site.urls),
    path("artworks/", include("artworks.urls")),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('auth/', include('accounts.urls')),


    # 🔹 모든 API는 /api/ 아래로 통합
    path('api/artworks/', include('artworks.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/reviews/', include('reviews.urls')),

    # 🔹 Swagger 및 Redoc
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),

    path('api/exhibition/', include('exhibition.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)