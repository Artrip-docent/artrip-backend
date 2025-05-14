from django.apps import AppConfig
from pymongo import MongoClient
from django.conf import settings

class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'

    def ready(self):
        try:
            client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=3000)
            client.server_info()
            print("✅ [MongoDB] 연결 성공")
        except Exception as e:
            print(f"❌ [MongoDB] 연결 실패: {e}")