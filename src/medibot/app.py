"""Streamlit web interface for MediBot."""

import logging

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from medibot.llm import build_rag_chain
from medibot.vectorstore import load_vectorstore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@st.cache_resource
def get_rag_chain():
    """Load vector store and build RAG chain (cached across reruns)."""
    vectorstore = load_vectorstore()
    return build_rag_chain(vectorstore)


def main() -> None:
    st.set_page_config(
        page_title="MediBot",
        page_icon=":hospital:",
        layout="wide",
    )

    # --- Disclaimer Modal ---
    if "disclaimer_accepted" not in st.session_state:
        st.session_state.disclaimer_accepted = False

    if not st.session_state.disclaimer_accepted:
        st.warning("⚠️ **MEDICAL DISCLAIMER**")
        st.markdown(
            """
            **This tool is for educational and reference purposes only.**

            It does not provide medical advice, diagnosis, or treatment recommendations.
            Always consult a licensed healthcare professional for medical decisions.
            """
        )
        if st.button("I Understand - Enter MediBot", type="primary", use_container_width=True):
            st.session_state.disclaimer_accepted = True
            st.rerun()
        st.stop()

    # --- Main Interface ---
    st.title("MediBot - Medical Reference Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Controls")
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")
        st.caption("Powered by RAG + Groq LLM")

    # Display chat history
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Feedback buttons for assistant messages
            if message["role"] == "assistant" and "feedback_key" in message:
                col1, col2 = st.columns([0.1, 0.9])
                with col1:
                    if st.button("👍", key=f"up_{message['feedback_key']}"):
                        st.toast("Response marked as helpful. Thank you!")
                    if st.button("👎", key=f"down_{message['feedback_key']}"):
                        st.toast("Response flagged. We'll improve this.")

    # Chat input
    prompt = st.chat_input("Ask a medical question...")

    if prompt:
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            rag_chain = get_rag_chain()

            # Convert chat history to LangChain message format
            chat_history = []
            for msg in st.session_state.messages[:-1]:
                if msg["role"] == "user":
                    chat_history.append(HumanMessage(content=msg["content"]))
                else:
                    chat_history.append(AIMessage(content=msg["content"]))

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                # Streaming response
                for chunk in rag_chain.stream({
                    "input": prompt,
                    "chat_history": chat_history,
                }):
                    if "answer" in chunk:
                        full_response += chunk["answer"]
                        message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)

                # Add context as citations
                if "context" in chunk:
                    with st.expander("📚 View Source Documents"):
                        for i, doc in enumerate(chunk["context"], 1):
                            source = doc.metadata.get("source", "Unknown")
                            snippet = doc.page_content[:300].replace("\n", " ")
                            st.markdown(f"**[{i}] {source}:** {snippet}...")

            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "feedback_key": f"fb_{len(st.session_state.messages)}",
            })

        except Exception as e:
            st.error(f"Error: {e}")
            logger.exception("Query failed")


if __name__ == "__main__":
    main()
