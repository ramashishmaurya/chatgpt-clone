
import os
from typing import Literal

from dotenv import load_dotenv

from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# pyrefly: ignore [missing-import]
from langchain_tavily import TavilySearch
from retriever import get_retriever
load_dotenv()


# ============================================================
# LLM
# ============================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
    streaming=True,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)


# ============================================================
# ROUTER
# ============================================================

router_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)


ROUTER_PROMPT = """
You are a query router.

Classify the user's question into exactly ONE of these categories:

1. CHAT
   Use this for normal conversation and questions that can be answered
   from general knowledge.

   Examples:
   - Hello
   - How are you?
   - What is AI?
   - Explain Python loops
   - What is the capital of France?
   - Tell me a joke

2. DOCUMENT
   Use this ONLY when the user is asking about information that is likely
   contained in their uploaded/private documents.

   Examples:
   - What does my uploaded document say about pricing?
   - Summarize my PDF
   - According to my document, what is the refund policy?
   - Find the employee leave policy in my uploaded files
   - What does the contract say about termination?

3. WEB
   Use this when the answer requires current, real-time, recent, or
   changing information.

   Examples:
   - What is Apple's stock price today?
   - What are today's news headlines?
   - What is the weather today?
   - Who won today's match?
   - What are the latest OpenAI updates?

IMPORTANT:
- Do NOT choose DOCUMENT just because the user asks a question.
- Normal/general knowledge questions are CHAT.
- DOCUMENT is only for private/uploaded document information.
- Current/recent/live information is WEB.

Return ONLY one word:

CHAT
DOCUMENT
WEB

User question:
{question}
"""


async def route_question(question: str) -> Literal["CHAT", "DOCUMENT", "WEB"]:
    """
    Decide whether we need:
    - CHAT     -> direct LLM
    - DOCUMENT -> Qdrant retrieval + LLM
    - WEB      -> Tavily + LLM
    """

    prompt = ChatPromptTemplate.from_template(ROUTER_PROMPT)

    chain = prompt | router_llm | StrOutputParser()

    result = await chain.ainvoke({
        "question": question
    })

    route = result.strip().upper()

    if "DOCUMENT" in route:
        return "DOCUMENT"

    if "WEB" in route:
        return "WEB"

    return "CHAT"


# ============================================================
# TAVILY
# ============================================================

def get_tavily_tool():
    """
    Initialize Tavily only when needed.
    """

    try:
        return TavilySearchResults(max_results=3)

    except Exception as e:
        print(f"Failed to initialize Tavily tool: {e}")
        return None


# ============================================================
# DOCUMENT RETRIEVAL
# ============================================================

async def retrieve_documents(
    session_id: str,
    question: str,
):
    """
    Search Qdrant only when the router decides DOCUMENT.
    """

    retriever = get_retriever(
        session_id=session_id,
        k=4,
    )

    documents = await retriever.ainvoke(question)

    if not documents:
        return ""

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    return context


# ============================================================
# HELPERS
# ============================================================

def normalize_content(content):
    """
    Gemini can sometimes return:
        "text"

    or:

        [
            {"type": "text", "text": "..."}
        ]
    """

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        text_blocks = []

        for block in content:

            if isinstance(block, dict):

                if "text" in block:
                    text_blocks.append(block["text"])

        if text_blocks:
            return "\n".join(text_blocks)

    return str(content)


# ============================================================
# SYSTEM PROMPTS
# ============================================================

CHAT_SYSTEM_PROMPT = """
You are a helpful and intelligent AI assistant.

Answer the user's question naturally and directly.

This is a normal conversation, so do NOT assume the user is asking
about uploaded documents.

Do not mention databases, Qdrant, retrieval, routing, tools, or
internal implementation details.

For current/recent information, use web search when it is available.
"""


DOCUMENT_SYSTEM_PROMPT = """
You are a helpful AI assistant answering questions using the user's
uploaded documents.

Use the document context below to answer the question.

Important rules:
- Prefer the provided document context when answering document-related questions.
- Do not invent information that is not supported by the context.
- If the answer cannot be found in the provided context, clearly say that
  the information was not found in the uploaded documents.
- You may use your general knowledge only when it helps explain information,
  but do not pretend it came from the user's documents.

Document context:
{context}
"""


WEB_SYSTEM_PROMPT = """
You are a helpful AI assistant.

The user is asking for current, recent, or changing information.

Use the web search results provided by the tool to answer accurately.

Do not mention internal tools, agents, routing, or implementation details.
"""


# ============================================================
# CHAT HANDLER
# ============================================================

async def answer_chat(question: str):
    """
    Normal conversation.

    IMPORTANT:
    No Qdrant call happens here.
    """

    messages = [
        SystemMessage(content=CHAT_SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]

    response = await llm.ainvoke(messages)

    return normalize_content(response.content)


# ============================================================
# DOCUMENT HANDLER
# ============================================================

async def answer_document(
    session_id: str,
    question: str,
):
    """
    Document question.

    Qdrant is called ONLY here.
    """

    context = await retrieve_documents(
        session_id=session_id,
        question=question,
    )

    if not context:
        context = "No relevant information was found in the uploaded documents."

    system_msg = SystemMessage(
        content=DOCUMENT_SYSTEM_PROMPT.format(
            context=context
        )
    )

    human_msg = HumanMessage(
        content=question
    )

    response = await llm.ainvoke([
        system_msg,
        human_msg,
    ])

    return normalize_content(response.content)


# ============================================================
# WEB HANDLER
# ============================================================

async def answer_web(question: str):
    """
    Current/recent information.

    Tavily is used only here.
    """

    tavily_tool = get_tavily_tool()

    if tavily_tool is None:

        # Fallback if Tavily is unavailable.
        response = await llm.ainvoke([
            SystemMessage(content=WEB_SYSTEM_PROMPT),
            HumanMessage(content=question),
        ])

        return normalize_content(response.content)

    # Search the web directly.
    search_results = await tavily_tool.ainvoke({
        "query": question
    })

    # Convert search results to text.
    if isinstance(search_results, list):

        web_context = "\n\n".join(
            str(result)
            for result in search_results
        )

    else:
        web_context = str(search_results)

    web_prompt = f"""
{WEB_SYSTEM_PROMPT}

Web search results:

{web_context}

User question:

{question}

Answer the user based on the search results.
"""

    response = await llm.ainvoke([
        SystemMessage(content=web_prompt),
        HumanMessage(content=question),
    ])

    return normalize_content(response.content)


# ============================================================
# MAIN ASK FUNCTION
# ============================================================

async def ask_question(
    session_id: str,
    question: str,
):
    """
    Main non-streaming function.

    Routing:

        CHAT
          -> LLM directly

        DOCUMENT
          -> Qdrant -> LLM

        WEB
          -> Tavily -> LLM
    """

    # --------------------------------------------------------
    # STEP 1: Route the question
    # --------------------------------------------------------

    route = await route_question(question)

    print(f"[ROUTER] {route}: {question}")

    # --------------------------------------------------------
    # STEP 2: CHAT
    # --------------------------------------------------------

    if route == "CHAT":

        return await answer_chat(
            question
        )

    # --------------------------------------------------------
    # STEP 3: DOCUMENT
    # --------------------------------------------------------

    if route == "DOCUMENT":

        return await answer_document(
            session_id=session_id,
            question=question,
        )

    # --------------------------------------------------------
    # STEP 4: WEB
    # --------------------------------------------------------

    if route == "WEB":

        return await answer_web(
            question
        )

    # Safety fallback
    return await answer_chat(
        question
    )


# ============================================================
# STREAMING
# ============================================================

async def stream_question(
    session_id: str,
    question: str,
):
    """
    Streaming version with the SAME routing logic.

    CHAT:
        No Qdrant

    DOCUMENT:
        Qdrant -> stream LLM

    WEB:
        Tavily -> stream LLM
    """

    # --------------------------------------------------------
    # STEP 1: Route
    # --------------------------------------------------------

    route = await route_question(question)

    print(f"[ROUTER] {route}: {question}")

    # ========================================================
    # CHAT STREAM
    # ========================================================

    if route == "CHAT":

        messages = [
            SystemMessage(
                content=CHAT_SYSTEM_PROMPT
            ),
            HumanMessage(
                content=question
            ),
        ]

        async for chunk in llm.astream(messages):

            if chunk.content:

                if isinstance(chunk.content, str):

                    yield chunk.content

                elif isinstance(chunk.content, list):

                    for block in chunk.content:

                        if (
                            isinstance(block, dict)
                            and "text" in block
                        ):
                            yield block["text"]

        return

    # ========================================================
    # DOCUMENT STREAM
    # ========================================================

    if route == "DOCUMENT":

        # Qdrant is called ONLY here.
        context = await retrieve_documents(
            session_id=session_id,
            question=question,
        )

        if not context:
            context = (
                "No relevant information was found "
                "in the uploaded documents."
            )

        system_msg = SystemMessage(
            content=DOCUMENT_SYSTEM_PROMPT.format(
                context=context
            )
        )

        human_msg = HumanMessage(
            content=question
        )

        async for chunk in llm.astream([
            system_msg,
            human_msg,
        ]):

            if chunk.content:

                if isinstance(chunk.content, str):

                    yield chunk.content

                elif isinstance(chunk.content, list):

                    for block in chunk.content:

                        if (
                            isinstance(block, dict)
                            and "text" in block
                        ):
                            yield block["text"]

        return

    # ========================================================
    # WEB STREAM
    # ========================================================

    if route == "WEB":

        tavily_tool = get_tavily_tool()

        if tavily_tool is None:

            async for chunk in llm.astream([
                SystemMessage(
                    content=WEB_SYSTEM_PROMPT
                ),
                HumanMessage(
                    content=question
                ),
            ]):

                if chunk.content:

                    if isinstance(chunk.content, str):
                        yield chunk.content

                    elif isinstance(chunk.content, list):

                        for block in chunk.content:

                            if (
                                isinstance(block, dict)
                                and "text" in block
                            ):
                                yield block["text"]

            return

        # ----------------------------------------------------
        # Tavily search
        # ----------------------------------------------------

        search_results = await tavily_tool.ainvoke({
            "query": question
        })

        if isinstance(search_results, list):

            web_context = "\n\n".join(
                str(result)
                for result in search_results
            )

        else:

            web_context = str(search_results)

        web_prompt = f"""
{WEB_SYSTEM_PROMPT}

Web search results:

{web_context}

User question:

{question}

Answer the user based on the search results.
"""

        async for chunk in llm.astream([
            SystemMessage(
                content=web_prompt
            ),
            HumanMessage(
                content=question
            ),
        ]):

            if chunk.content:

                if isinstance(chunk.content, str):

                    yield chunk.content

                elif isinstance(chunk.content, list):

                    for block in chunk.content:

                        if (
                            isinstance(block, dict)
                            and "text" in block
                        ):
                            yield block["text"]

        return


