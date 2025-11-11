from utils.common import processStartMsg, processEndMsg
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
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
CHAT_MODEL = os.getenv("CHAT_MODEL")

sourcePath = os.path.join(os.getcwd(), "backend/documentSource/unprocessed/pdf")
targetPath = os.path.join(os.getcwd(), "backend/documentSource/processed/pdf")

# --------------------------------------------------------------------------------------------------

def custom_loader(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return PyPDFLoader(file_path)
    

def moveProcessfile():
    print("Processced File(s):")
    for item in os.listdir(sourcePath):
        if item.lower().endswith(('.pdf')):
            print("  - "+item)
            src_path = os.path.join(sourcePath, item)
            dest_path = os.path.join(targetPath, item)

            # Move file or directory
            shutil.move(src_path, dest_path)

    
def UpdatePdfFileVector():
    processStartMsg("PDF file start updating in vector database...")
    
    #print(sourcePath)
    if os.listdir(sourcePath):
        clientObj = getQdrantClient()
        #----- Data/ Folder contains all PDF files ---------------
        loader = DirectoryLoader(
                path=sourcePath,              # folder path
                glob="*.pdf",                 # load only PDF files
                loader_cls=PyPDFLoader        # use PyPDFLoader for each file
                )
        documents = loader.load()
        print(f"Loaded {len(documents)} PDF pages from source folder")
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        finalDocContent = splitter.split_documents(documents)
        print(f"Split into {len(finalDocContent)} text chunks")
        #----- Initialize embedding model ---
        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, openai_api_key=OPENAI_API_KEY)
        
        #-----Store documents in Qdrant Cloud ---------------
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


    processEndMsg("")

    return True
    
def VerifyDBContent_OLD(queryParams):

   
    clientObj = getQdrantClient()
    #----- Connect to Qdrant Cloud ---
    # --- Initialize OpenAI embeddings (for query search) ---
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, openai_api_key=OPENAI_API_KEY)    
       
    vectorstore = QdrantVectorStore(
        client=clientObj,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )
    
    #print(f"✅ Connected to Qdrant collection: {COLLECTION_NAME}")

    # --- Option 1: Retrieve all documents metadata ---
    #print("Fetching sample document metadata...")
    #collections = clientObj.get_collections()
    #print("Available Collections:", [c.name for c in collections.collections])
    #queryParams = "What are Childcare Exit/Termination policy?"
    print(f"Searching for: '{queryParams}'")
    results = vectorstore.similarity_search(queryParams, k=3)
    for i, doc in enumerate(results, start=1):
        print(f"\nResult {i}")
        #print(f"Source: {doc.metadata.get('source', 'unknown')}")
        print(f"Content:\n{doc.page_content[:200]}...")



def RetrievalQADBContent(queryParams):
    
    
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnableMap, RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser

    clientObj = getQdrantClient()
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    llm = ChatOpenAI(model=CHAT_MODEL)
    # Vectorstore retriever
    vectorstore = QdrantVectorStore(
        client=clientObj,
        collection_name=COLLECTION_NAME,
        embedding=embeddings
    )
    context = vectorstore.as_retriever(search_kwargs={"k": 3})
    # Build retrieval-based prompt manually
    prompt = ChatPromptTemplate.from_template("""
            You are an HR assistant chatbot.
            Use the pieces of information provided in the context to answer user's question accurately.
            Answer ONLY from the provided transcript context.
            If you dont know the answer, just say that you dont know, dont try to make up an answer. 
            Dont provide anything out of the given context

            Context: {context}
            Question: {question}
                                              
            """)
    # Compose retrieval + LLM pipeline
    ragChain = (
            {"context": context, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )   
    # Run query
    
    response = ragChain.invoke(queryParams)
    print(response)

    