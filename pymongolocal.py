import pymongo

# Connections
local_client = pymongo.MongoClient("mongodb://localhost:27017/")
atlas_client = pymongo.MongoClient("mongodb+srv://isamoma_db_user:323821442%40Isa@cluster0.wxg60qw.mongodb.net/celebhub_db?retryWrites=true&w=majority")

db_name = "isamoma_db_" 

def sync_to_atlas():
    local_db = local_client[db_name]
    atlas_db = atlas_client[db_name]
    
    # Get all collection names from local
    collections = local_db.list_collection_names()
    
    for col_name in collections:
        print(f"Syncing {col_name}...")
        docs = list(local_db[col_name].find())
        if docs:
            # Clear Atlas collection first to avoid duplicates (Optional)
            atlas_db[col_name].delete_many({}) 
            # Insert docs into Atlas
            atlas_db[col_name].insert_many(docs)
            print(f"✅ Moved {len(docs)} documents to Atlas.")

if __name__ == "__main__":
    sync_to_atlas()