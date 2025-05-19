# Import necessary libraries
import streamlit as st
import google.generativeai as genai
import os
import time # Optional: to simulate typing or processing delay

# --- Configuration ---
# IMPORTANT: Set your API key as an environment variable for security.
# Streamlit Cloud ya local environment mein is tarah set karna best hai.
# Example local command: export GOOGLE_API_KEY="YOUR_API_KEY" (Linux/macOS)
# set GOOGLE_API_KEY="YOUR_API_KEY" (Windows Command Prompt)
# $env:GOOGLE_API_KEY="YOUR_API_KEY" (Windows PowerShell)

# Check for API key in environment variables
api_key = os.getenv("GOOGLE_API_KEY")

# Agar API key nahi mili, toh user ko input karne ka option do
if not api_key:
    st.warning("Google API key environment variable ('GOOGLE_API_KEY') not found.", icon="⚠️")
    api_key = st.text_input("Enter your Google API Key:", type="password")
    # Agar user ne abhi bhi key enter nahi ki aur aage badhne ki koshish ki, toh ruk jao
    if not api_key:
        st.stop() # Stop execution until API key is provided

try:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Error configuring Google Generative AI API: {e}")
    st.stop() # Stop if API configuration fails

# --- Model Initialization ---
# Choose a Gemini model.
# 'gemini-1.5-flash' ya 'gemini-pro' usually safe bets hain.
# Tumhare code mein 'gemini-2.0-flash' tha, woh use kar sakte hain agar available hai.
# Agar error aaye toh 'gemini-1.5-flash' try kar sakte ho.
MODEL_NAME = "gemini-1.5-flash" # Using a generally available model

# Initialize model and chat session in Streamlit's session state
# Taki page reload pe state maintain rahe
if "chat_session" not in st.session_state:
    try:
        model = genai.GenerativeModel(model_name=MODEL_NAME)
        st.session_state.chat_session = model.start_chat(history=[])
    except Exception as e:
        st.error(f"Error initializing the model or chat session: {e}")
        st.stop()

# Store chat history in Streamlit's session state
# Har message ko store karenge display karne ke liye
if "messages" not in st.session_state:
    st.session_state.messages = [] # List of {"role": ..., "content": ...}

# --- Streamlit UI ---
st.title("🤖 Gemini Chatbot Interface")

st.write("""
Yeh ek simple chatbot interface hai jo Google Gemini API use karta hai.
Apne sawal poochiye! 👋
""")

# Display previous messages
# Har message ko chat bubble ki tarah dikhayenge
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input ---
# User se input lene ke liye
prompt = st.chat_input("Say something...")

# Agar user ne kuch type kiya aur Enter dabaya
if prompt:
    # Add user message to history and display it immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send user message to the model and get the response
    # Use the chat session stored in state
    try:
        # Optional: Add a thinking message or spinner
        with st.chat_message("model"):
            with st.spinner("Thinking..."):
                # Pass the prompt to the existing chat session
                response = st.session_state.chat_session.send_message(prompt)
                # time.sleep(1) # Simulate delay if needed

        # Display assistant response
        # Check if the response is valid before displaying
        if response and hasattr(response, 'text') and response.text:
             with st.chat_message("model"):
                 st.markdown(response.text)
             # Add assistant response to history
             st.session_state.messages.append({"role": "model", "content": response.text})
        else:
             error_message = "I'm sorry, I couldn't generate a response."
             if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                 error_message += f"\nPrompt feedback: {response.prompt_feedback}"
             with st.chat_message("model"):
                 st.error(error_message)
             st.session_state.messages.append({"role": "model", "content": error_message})

    except Exception as e:
        error_message = f"An error occurred: {e}"
        st.error(error_message)
        st.session_state.messages.append({"role": "model", "content": error_message})