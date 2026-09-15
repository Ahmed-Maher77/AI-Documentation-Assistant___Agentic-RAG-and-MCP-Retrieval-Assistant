import streamlit as st
import json

from langchain_agent import ask_agent



# Page configuration
st.set_page_config(
    page_title="LangChain Documentation Assistant",
    page_icon="📚",
    layout="centered"
)


# Session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm your LangChain documentation assistant. "
                       "Ask me anything about LangChain, and I'll provide answers based on the official documentation."
        }
    ]


# Sidebar
with st.sidebar:
    st.title("📚 LangChain Assistant")

    st.divider()

    # Clear chat
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # Save chat
    st.subheader("Chat History")

    if st.button("💾 Save Chat", use_container_width=True):
        with open("chat.json", "w", encoding="utf-8") as file:
            json.dump(
                st.session_state.messages,
                file,
                ensure_ascii=False,
                indent=4
            )

        st.success("Chat saved successfully!")

    # Load chat
    if st.button("📂 Load Chat", use_container_width=True):
        try:
            with open("chat.json", "r", encoding="utf-8") as file:
                st.session_state.messages = json.load(file)
            st.success("Chat loaded successfully!")

            st.rerun()

        except FileNotFoundError:
            st.error("No saved chat found.")

    st.divider()
    st.caption(
        "© 2026 Developed by [Ahmed Maher](https://ahmedmaher-portfolio.vercel.app/)"
    )


# =============== Main UI 
st.title("📚 LangChain Documentation Assistant")

st.caption(
    "Ask questions about LangChain and get answers from its documentation."
)



# Display conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# User input
user_query = st.chat_input(
    "Ask me anything about LangChain documentation..."
)


if user_query:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_query
    })

    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_query)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Searching LangChain documentation..."):
            try:
                response = ask_agent(
                    st.session_state.messages
                )
            except Exception as exc:
                st.error(f"Unable to answer right now: {exc}")
                response = "I couldn't generate a response because the model backend isn't available. Please start Ollama and ensure the model is installed."

        # Render Markdown
        st.markdown(response)

    # Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })