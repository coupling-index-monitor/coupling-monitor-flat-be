from app.core.database import db_manager


def fetch_new_traces_since_last_sync():
    """
    Fetch all new traces since the last sync date.
    """
    trace_collection = db_manager.get_trace_collection()
    last_sync_date = get_last_sync_date()

    query = {}
    if last_sync_date:
        query["spans.startTime"] = {"$gt": last_sync_date}  # Directly compare numeric timestamps

    return list(trace_collection.find(query, {"_id": 0}))


def update_last_sync_date(last_sync_date):
    """
    Update the last sync date in the trace_collection_updates collection.
    """
    collection = db_manager.get_trace_collection_updates_collection()
    collection.update_one(
        {},
        {"$set": {"last_sync_date": last_sync_date}},
        upsert=True
    )


def get_last_sync_date():
    """
    Retrieve the last sync date from the trace_collection_updates collection.
    """
    collection = db_manager.get_trace_collection_updates_collection()
    record = collection.find_one()
    return int(record["last_sync_date"]) if record else None
