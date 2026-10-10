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
        
        # Inject custom Metadata for Filtering!
        for doc in documents:
            doc.metadata["source"] = filename
            doc.metadata["file_type"] = suffix.replace(".", "")
            doc.metadata["category"] = "confidential" # Example tag for demonstration
            
        # ==========================================
        # MULTIMODAL RAG IMPLEMENTATION
        # ==========================================
        if suffix == ".pdf":
            try:
                import fitz
                import base64
                from langchain_core.messages import HumanMessage
                from langchain_ollama import ChatOllama
                from langchain_core.documents import Document
                
                print("[Multimodal RAG] Extracting images from PDF...")
                pdf_doc = fitz.open(tmp_path)
                llava = ChatOllama(model="llava", temperature=0.0)
                
                for page_num in range(len(pdf_doc)):
                    page = pdf_doc.load_page(page_num)
                    image_list = page.get_images(full=True)
                    
                    for img_index, img in enumerate(image_list):
                        xref = img[0]
                        base_image = pdf_doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        
                        encoded_image = base64.b64encode(image_bytes).decode("utf-8")
                        
                        print(f"[Multimodal RAG] Analyzing image {img_index+1} on page {page_num+1} with LLaVA...")
                        message = HumanMessage(
                            content=[
                                {"type": "text", "text": "Describe this image in detail. If it is a chart or table, explain the data. If it's a logo or decorative, just say 'Decorative image'."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                            ]
                        )
                        
                        response = llava.invoke([message])
                        summary = response.content.strip()
                        
                        if "decorative" not in summary.lower():
                            documents.append(Document(
                                page_content=f"[MULTIMODAL IMAGE SUMMARY - Page {page_num+1}]: {summary}",
                                metadata={"source": filename, "type": "image_summary"}
                            ))
                            print(f"[Multimodal RAG] Saved image summary: {summary[:50]}...")
            except Exception as e:
                print(f"[Multimodal RAG] Failed to process images: {e}")
            
    finally:
        os.unlink(tmp_path)

    splitter = RecursiveCharacterTextSplitter(
       chunk_size=500,
       chunk_overlap=50
    )
    
    chunks = splitter.split_documents(documents)
    
    # ==========================================
    # CONTEXTUAL CHUNKING RAG IMPLEMENTATION
    # ==========================================
    from llm_factory import get_llm
    
    # 1. Get a sample of the document to generate context
    full_text = " ".join([doc.page_content for doc in documents])
    
    try:
        # 2. Ask Ollama to generate a short contextual summary
        llm = get_llm(temperature=0.0)
        prompt = f"Write a 1-sentence summary of this document to provide context for isolated excerpts: {full_text[:3000]}"
        context_summary = llm.invoke(prompt).content.strip()
        
        context_prefix = f"\n[DOCUMENT CONTEXT: {context_summary}]\n"
        print("Generated Contextual Prefix:", context_prefix)
        
        # 3. Prepend this context to EVERY single chunk before saving to Vector Database!
        for chunk in chunks:
            chunk.page_content = context_prefix + chunk.page_content
            
    except Exception as e:
        print("Failed to generate contextual chunking summary:", e)

    return chunks