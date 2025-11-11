import os
from dotenv import load_dotenv
from qdrantDbConnection import getQdrantClient
from qdrant_client.http.models import Distance, VectorParams
from utils.common import processStartMsg, processEndMsg

#from qdrant_client import QdrantClient
#from qdrant_client.http.models import Distance, VectorParams

# Load environment variables
load_dotenv()


QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME =  os.getenv("COLLECTION_NAME")


def CreateDBCollection(vectorSize: int = 3072):
    processStartMsg("CreateDBCollection process started...")
    
    clientObj = getQdrantClient()
     

    # --- Create the collection ---
    try:
        if not __collection_exists(COLLECTION_NAME):
                
            clientObj.recreate_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(
                            size=vectorSize, 
                            distance=Distance.COSINE # Options: COSINE, DOT, EUCLID
                        )
            )
            print(f"Collection '{COLLECTION_NAME}' created.")
        else:
            print(f"Collection '{COLLECTION_NAME}' already exists.")
    
    except Exception as e:
        print(f"Error creating collection: {e}")

    processEndMsg("")


def DeleteDBCollection():
    processStartMsg("DeleteDBCollection process started...")
    clientObj = getQdrantClient()

    collections_response = clientObj.get_collections()
    collections = collections_response.collections
    if(len(collections) ==0):
        print(f"No any collection exist")
    else:
        print(f"Collection list:")
        for c in clientObj.get_collections().collections:
            print(f"     --- {c.name}")
            print(f"=======================================")
            print(f"Start Deleting all collections:")
            print(f"=======================================")
       

        for c in clientObj.get_collections().collections:
            clientObj.delete_collection(c.name)
            print(f"Deleted collection: {c.name}")

    processEndMsg("")        

def ListAllDBCollection():
    processStartMsg("ListAllDBCollection process started...")
    clientObj = getQdrantClient()
    collections_response = clientObj.get_collections()
    collections = collections_response.collections
    if(len(collections) ==0):
        print(f"No any collection exist")
    else:
        print(f"Collection List:")
        for c in clientObj.get_collections().collections:
            collectionCount = clientObj.count(collection_name=c.name).count
            print(f"     --- {c.name} has {collectionCount} vectors stored")

    processEndMsg("")
            

def __collection_exists(collection_name: str) -> bool:
    """
    Check if a Qdrant collection exists.
    
    Args:
        collection_name (str): Name of the collection to check.
    
    Returns:
        bool: True if collection exists, False otherwise.
    """
    clientObj = getQdrantClient()
    collections = clientObj.get_collections().collections
    return any(c.name == collection_name for c in collections)