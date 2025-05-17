from pymongo import MongoClient
from django.conf import settings
from datetime import datetime
def get_mongo_collection():
    """
    MongoDB 컬렉션 객체를 반환합니다.
    ex) get_mongo_collection().insert_one({...})
    """
    client = MongoClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB]
    collection = db[settings.MONGODB_COLLECTION]
    return collection

def save_chat_log(user_message, response_text, user_id=None, exhibition_id=None, artwork_id=None):
    collection = get_mongo_collection()

    history_entry = {
        "question": user_message,
        "answer": response_text
    }

    collection.update_one(
        {
            "user_id": user_id,
            "exhibition_id": exhibition_id,
            "artwork_id": artwork_id
        },
        {
            "$push": {"history": history_entry},
            "$set": {"time": datetime.utcnow()},
            "$setOnInsert": {
                "user_id": user_id,
                "exhibition_id": exhibition_id,
                "artwork_id": artwork_id
            }
        },
        upsert=True
    )