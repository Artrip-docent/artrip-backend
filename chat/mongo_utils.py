from pymongo import MongoClient
from django.conf import settings

def get_mongo_collection():
    """
    MongoDB 컬렉션 객체를 반환합니다.
    ex) get_mongo_collection().insert_one({...})
    """
    client = MongoClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB]
    collection = db[settings.MONGODB_COLLECTION]
    return collection
