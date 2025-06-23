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

def save_chat_log(user_message, response_text, user_id, exhibition_id, artwork_id):
    # 매개변수 출력
    print(f"[DEBUG] user_message={user_message!r}")
    print(f"[DEBUG] response_text={response_text!r}")
    print(f"[DEBUG] user_id={user_id!r}, exhibition_id={exhibition_id!r}, artwork_id={artwork_id!r}")

    collection = get_mongo_collection()

    history_entry = {
        "question": user_message,
        "answer": response_text
    }

    result = collection.update_one(
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
    # update_one 결과 출력 (수정된 문서 수 등 확인 가능)
    print(
        f"[DEBUG] matched_count={result.matched_count}, modified_count={result.modified_count}, upserted_id={result.upserted_id}")
    # 완료 메시지
    print("완료되었습니다.")

def save_info(info_text, user_id=None, exhibition_id=None, artwork_id=None):
    collection = get_mongo_collection()

    filter_query = {
        "user_id": int(user_id),
        "artwork_id": int(artwork_id),
        "exhibition_id": int(exhibition_id),
    }

    existing_doc = collection.find_one(filter_query)

    if existing_doc:
        collection.update_one(
            filter_query,
            {"$set": {
                "information": info_text,
                "time": datetime.utcnow()
            }}
        )
    else:
        collection.insert_one({
            "user_id": int(user_id),
            "artwork_id": int(artwork_id),
            "exhibition_id": int(exhibition_id),
            "information": info_text,
            "history": [],
            "time": datetime.utcnow()
        })

def get_context(user_id=None, exhibition_id=None, artwork_id=None):
    collection = get_mongo_collection()

    query = {
        "user_id": user_id,
        "exhibition_id": exhibition_id,
        "artwork_id": artwork_id
    }

    doc = collection.find_one(query)
    if not doc or "history" not in doc:
        return []

    return doc["history"]
