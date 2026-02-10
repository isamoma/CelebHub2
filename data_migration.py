import pymongo
from pymongo.errors import BulkWriteError

# --- Configuration ---
LOCAL_URI = "mongodb://localhost:27017/"
# Using the URI that you confirmed worked in the previous test
ATLAS_URI = "mongodb+srv://isamoma_db_user:323831442Isa@cluster0.wxg60qw.mongodb.net/celebhub_db?retryWrites=true&w=majority"

def migrate():
    try:
        local_client = pymongo.MongoClient(LOCAL_URI)
        atlas_client = pymongo.MongoClient(ATLAS_URI)
        
        # Source and Destination Databases
        local_db = local_client['isamoma_db_']
        atlas_db = atlas_client['celebhub_db']

        print(f"--- Starting Migration from Local to Atlas ---")

        for collection_name in local_db.list_collection_names():
            if collection_name.startswith("system."):
                continue  # Skip internal mongo collections
                
            print(f"📦 Processing: {collection_name}...")
            
            # 1. Fetch data from local
            data = list(local_db[collection_name].find())
            
            if not data:
                print(f"   - Collection is empty. Skipping.")
                continue

            # 2. Clear destination (optional, prevents duplicates)
            atlas_db[collection_name].delete_many({})

            # 3. Insert into Atlas
            try:
                atlas_db[collection_name].insert_many(data)
                print(f"   ✅ Successfully moved {len(data)} documents.")
            except BulkWriteError as bwe:
                print(f"   ❌ Error inserting into {collection_name}: {bwe.details}")

        print(f"\n✨ Migration Complete! Your cloud database is now ready.")

    except Exception as e:
        print(f"❌ Migration Failed: {e}")

if __name__ == "__main__":
    migrate()