from pymongo import MongoClient

# MongoDB database connection
def get_mongo_client(uri="mongodb://localhost:27017/"):
    return MongoClient(uri)

client = get_mongo_client()
db = client["academicworld"]
collection = db["publications"]


def get_top_keywords_for_selected_years(start_year, end_year, n=8):
    client = get_mongo_client()
    pipeline = [
        {"$unwind":"$keywords"},
        {"$match": {"year": {"$gte": start_year, "$lte": end_year}}},
        {"$group":{"_id":"$keywords.name","pub_cnt":{"$sum":1}}},
        {"$sort":{"pub_cnt":-1}},
        {"$limit":8}
    ]
    
    result = list(collection.aggregate(pipeline))
    client.close()
    return result