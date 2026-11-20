import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
MONGO_URI = os.getenv("MONGODB_URI", "").strip()

client = None
db = None
sos_collection = None

# In-memory fallback if MongoDB is not configured or unreachable
_in_memory_sos_logs = []

if MONGO_URI and not MONGO_URI.startswith("replace_with"):
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=4000)
        client.admin.command("ping")
        db_name = os.getenv("MONGODB_DATABASE", "rakshai_db")
        coll_name = os.getenv("MONGODB_SOS_COLLECTION", "sos_logs")
        db = client[db_name]
        sos_collection = db[coll_name]
        print(f"Connected to MongoDB successfully: db={db_name}, coll={coll_name}")
    except (ConfigurationError, ConnectionFailure, Exception) as exc:
        print(f"MongoDB connection warning: {exc}. Using fallback log storage.")
        client = None
        db = None
        sos_collection = None
else:
    print("MongoDB is not configured; using local log storage.")


def log_sos_event(event_data):
    """Save an SOS event to MongoDB or local memory storage."""
    global _in_memory_sos_logs
    if sos_collection is not None:
        try:
            res = sos_collection.insert_one(dict(event_data))
            return str(res.inserted_id)
        except Exception as e:
            print(f"MongoDB log error: {e}")
    _in_memory_sos_logs.insert(0, dict(event_data))
    if len(_in_memory_sos_logs) > 100:
        _in_memory_sos_logs.pop()
    return "local"


def get_sos_events(limit=20):
    """Retrieve recent SOS alert events."""
    if sos_collection is not None:
        try:
            records = list(sos_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))
            return records
        except Exception as e:
            print(f"MongoDB read error: {e}")
    return _in_memory_sos_logs[:limit]
