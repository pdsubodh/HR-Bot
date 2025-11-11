import streamlit as st
from PIL import Image




st.set_page_config(layout="wide")
pages = {
    "🏠 | ChatBot": [
        st.Page("_chat.py", title="Chat" ),        
       # st.Page("ViewFile.py", title="View Knowledgebase Data"),
       # st.Page("UploadFile.py", title="Update Knowledgebase" ),
    ],
    "Sentiment Analysis": [
        st.Page("_soon.py", title="Sentiment Analysis"),   
             
    ],
    
}

pg = st.navigation(pages, position="top")
pg.run()