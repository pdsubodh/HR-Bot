import streamlit as st
import time
from datetime import datetime
from frontutils.responseGeneration import ResponseGeneration
from frontutils.helper import GetLastChatHistory



# --- Page setup ---
st.set_page_config(page_title="HR | Enterprise - ChatBot", page_icon="💬", layout="wide")

# --- Custom CSS for WhatsApp-like look ---
st.markdown("""
    <style>
    body {
        background-color: #ECE5DD;
    }
    .chat-container {
        max-width: 750px;
        margin: auto;
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        height: 75vh;
        overflow-y: auto;
        border: 1px solid red;
    }
    .message {
        padding: 10px 15px;
        border-radius: 15px;
        margin: 8px 0;
        display: inline-block;
        max-width: 75%;
        word-wrap: break-word;
        position: relative;
    }
    .user-msg {
        background-color: #DCF8C6;
        text-align: right;
        float: right;
        clear: both;
    }
    .bot-msg {
        background-color: #FFFFFF;
        border: 1px solid #ddd;
        text-align: left;
        float: left;
        clear: both;
    }
    .timestamp {
        display: block;
        font-size: 0.7rem;
        color: #888;
        margin-top: 3px;
        text-align: right;
    }
    .msg-row {
        display: flex;
        align-items: flex-end;
        margin-bottom: 10px;
    }
    .user-row {
        justify-content: flex-end;
    }
    .bot-row {
        justify-content: flex-start;
    }
    .avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        margin: 0 8px;
    }
    .chat-input {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #f0f0f0;
        padding: 10px;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

original_title = '<p style=" font-size: 1.5rem; font-weight: bold;">HR | Enterprise - ChatBot</p>'
st.markdown(original_title, unsafe_allow_html=True)


# --- Initialize chat history ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Placeholder backend function ---
def get_rag_response(query: str) -> str:
    #st.write("Generating response...")  

    # ✅ Define limited memory (last 3 conversation turns only)
    
    lastChatContext = GetLastChatHistory(3)
    #st.write("DEBUG chat_history:", st.session_state.chat_history)
    response = ResponseGeneration(query, lastChatContext)
    #response = "BOT response:: " + query
    #time.sleep(5)  # Simulate processing delay    
    return response

# --- Chat container ---
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-containers">', unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
                <div class="msg-row user-row">
                    <div class="message user-msg">
                        {msg['content']}
                        <span class="timestamp">{msg['time']}</span>
                    </div>
                    <img src="https://cdn-icons-png.flaticon.com/128/1077/1077012.png" class="avatar">
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="msg-row bot-row">
                    <img src="https://cdn-icons-png.flaticon.com/512/4712/4712035.png" class="avatar">
                    <div class="message bot-msg">
                        {msg['content']}
                        <span class="timestamp">{msg['time']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- Chat input section (fixed bottom) ---
st.markdown('<div class="chat-input">', unsafe_allow_html=True)
user_input = st.chat_input("Type your message...")

if user_input:
    # Store user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "time": datetime.now().strftime("%H:%M")
    })

    st.markdown(f"""
                <div class="msg-row user-row">
                    <div class="message user-msg">
                        {user_input}
                        <span class="timestamp">{datetime.now().strftime("%H:%M")}</span>
                    </div>
                    <img src="https://cdn-icons-png.flaticon.com/128/1077/1077012.png" class="avatar">
                </div>
            """, unsafe_allow_html=True)

    # Display “typing...” spinner
    with st.spinner("🤖 Bot is typing..."):

        full_response = get_rag_response(user_input)

        # Typing animation (word by word)
        response_placeholder = st.empty()
        typed_text = ""
        for word in full_response.split():
            typed_text += word + " "
            response_placeholder.markdown(f"""
                <div class="msg-row bot-row">
                    <img src="https://cdn-icons-png.flaticon.com/512/4712/4712035.png" class="avatar">
                    <div class="message bot-msg">
                        {typed_text.strip()}
                        <span class="timestamp">{datetime.now().strftime("%H:%M")}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            time.sleep(0.04)

        # Finalize bot response
        st.session_state.chat_history.append({
            "role": "bot",
            "content": full_response,
            "time": datetime.now().strftime("%H:%M")
        })

    # Force UI refresh
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
