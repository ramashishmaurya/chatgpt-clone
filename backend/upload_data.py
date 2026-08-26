import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_and_split(file_bytes:bytes, filename: str):
    suffix = os.path.splitext(filename)[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes) 
        tmp_path = tmp.name

    try:
        if suffix == ".pdf":
            loader = PyPDFLoader(tmp_path)
        elif suffix == ".docx":
            loader = Docx2txtLoader(tmp_path)
        elif suffix == ".txt":
            loader = TextLoader(tmp_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        documents = loader.load()  
    finally: 
        os.unlink(tmp_path)

    splitter = RecursiveCharacterTextSplitter(
       chunk_size=500,
       chunk_overlap=50
    )


    return splitter.split_documents(documents)