import os
from dotenv import load_dotenv

load_dotenv()

# pyrefly: ignore [missing-import]
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
)

response = llm.invoke("Explain RAG in simple words")

print(response.content)


