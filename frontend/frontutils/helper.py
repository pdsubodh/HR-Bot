import streamlit as st
    
def GetLastChatHistory(turnCount):

    lastMsgs = st.session_state.chat_history[-(turnCount*2):]  # 1 turn = user + bot
    formatted = []
    for msg in lastMsgs:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role.lower() == "user":
            formatted.append(f"Human: {content}")
        else:
            formatted.append(f"AI: {content}")
    return "\n".join(formatted)
