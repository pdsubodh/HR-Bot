from utils.common import processStartMsg, processEndMsg
from langchain_community.document_loaders import DirectoryLoader, TextLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrantDbConnection import getQdrantClient


import shutil
import os
from dotenv import load_dotenv
load_dotenv()


# Load credentials & Configurations ---------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

sourcePath = os.path.join(os.getcwd(), "backend/documentSource/unprocessed/txt")
targetPath = os.path.join(os.getcwd(), "backend/documentSource/processed/txt")

# --------------------------------------------------------------------------------------------------

    

def moveProcessfile():
    print("Processced File(s):")
    for item in os.listdir(sourcePath):
        if item.lower().endswith(('.txt')):
            print("  - "+item)
            src_path = os.path.join(sourcePath, item)
            dest_path = os.path.join(targetPath, item)

            # Move file or directory
            shutil.move(src_path, dest_path)

def UpdateTextFileVector():
    processStartMsg("Text file start updating in vector database...")
    try:
        if os.listdir(sourcePath):
                clientObj = getQdrantClient()
                loader = DirectoryLoader(
                sourcePath,
                glob="*.txt",  # load only txt files    
                loader_cls=TextLoader
                )
                documents = loader.load()
                print(f"Loaded {len(documents)} text pages from source folder")
                splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                finalDocContent = splitter.split_documents(documents)
                print(f"Split into {len(finalDocContent)} text chunks")
                embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, openai_api_key=OPENAI_API_KEY)
                # 4️⃣ Upload documents to Qdrant
                vectorstore = QdrantVectorStore(
                            client=clientObj,
                            collection_name=COLLECTION_NAME,
                            embedding=embeddings,
                            )
                vectorstore.add_documents(finalDocContent)
                print(f"Successfully stored {len(documents)} documents in collection: {COLLECTION_NAME}")

                #----- Move File(s) in Processed folder ---------------
                moveProcessfile()     
        else:
            print("Folder is empty: " +sourcePath)

    except Exception as e:
        print(f"Error creating collection: {e}")

    processEndMsg("")
