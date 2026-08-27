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
    temperature=0,
    google_api_key=os.getenv(
        "GOOGLE_API_KEY"
    ),
)


prompt = ChatPromptTemplate.from_template(
    """
You are a document question-answering assistant.

Answer the user's question ONLY using the
provided document context.

If the answer cannot be found in the context,
say exactly:

"I couldn't find this information in the document."

Do NOT use your general knowledge.

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

    # No documents found
    if not documents:

        return (
            "I couldn't find this information "
            "in the document."
        )

    # Combine chunks
    context = "\n\n".join(
        document.page_content
        for document in documents
    )

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


