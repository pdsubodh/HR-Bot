from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrantDbConnection import getQdrantClient
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
import re

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

# --------------------------------------------------------------------------------------------------

def ResponseGeneration(queryParams, lastChatContext):
    
    """
    Generate response based on query. 
    For greetings like hi/hello, respond warmly without LLM cost.
    """

    # --- Handle greetings directly (saves API calls) ---
    greetingInputs = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    normalizedInput = queryParams.strip().lower()
    pattern = r"\b(?:{})\b".format("|".join(map(re.escape, greetingInputs)))
    if re.search(pattern, normalizedInput):
        return "Hey there! 😊 It’s great to see you. How can I help you today?"


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
    contextDoc = context.invoke(queryParams)
    #print(contextDoc)
    #import streamlit as st
    #st.write("DEBUG chat_history:", contextDoc)
    
    
    #docs = context.invoke(queryParams)
    #st.write(docs)
    #exit(1)
    # Build final combined context
    #fullContext = f"Conversation History:\n{lastChatContext}\n\nRetrieved Context:\n{context}"
    #fullContext = context
    
    
    #exit(1)
    # Build retrieval-based prompt manually
    prompt = ChatPromptTemplate.from_template("""
            You are an HR assistant chatbot.
            Use both the conversation history and the retrieved context to answer user's question accurately.            
            Answer ONLY from the provided transcript context.
            If you dont know the answer, just say that you dont know, dont try to make up an answer. 
            Dont provide anything out of the given context
            history: {history}
                                              
            Context: {context}
                                              
            Question: {question}
                                              
            """)
    # Compose retrieval + LLM pipeline
    ragChain = (
            {
                "history": RunnableLambda(lambda _: lastChatContext),
                "context": RunnableLambda(lambda _: contextDoc),
                 "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )   
    # Run query
    
    response = ragChain.invoke(queryParams)
    return response
    

    