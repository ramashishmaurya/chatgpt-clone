import os

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
)

from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv
load_dotenv()


from retriever import get_retriever

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3, # Slightly increased temperature for more natural conversational responses
    google_api_key=os.getenv(
        "GOOGLE_API_KEY"
    ),
)


prompt = ChatPromptTemplate.from_template(
    """
You are a helpful and intelligent AI assistant. 

If document context is provided below, try to use it to answer the user's question. 
If the answer cannot be found in the context, or if no context is provided, you should answer the question using your general knowledge.

Document context:
{context}

User question:
{question}

Answer:
"""
)


async def ask_question(
    session_id: str,
    question: str,
):
    
    retriever = get_retriever(
        session_id=session_id,
        k=4,
    ) # retrives the top documents 4 
    

    # Search Qdrant
    documents = await retriever.ainvoke(
        question
    )

    # Combine chunks (will be empty string if no documents are found)
    context = "\n\n".join(
        document.page_content
        for document in documents
    )
    
    if not context:
        context = "No document uploaded or no relevant information found."
    
    # Create prompt
    messages = prompt.format_messages(
        context=context,
        question=question,
    )

    # Ask Gemini
    response = await llm.ainvoke(
        messages
    )

    return response.content
