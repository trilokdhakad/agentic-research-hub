from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def process_file(file_path: str, filename: str):
    # Route to the correct parser based on file extension
    if filename.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif filename.endswith(".txt"):
        loader = TextLoader(file_path)
    else:
        raise ValueError("Unsupported file type")
        
    documents = loader.load()
    
    for doc in documents:
        doc.metadata["source"] = filename

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50,
        length_function=len
    )
    
    chunks = text_splitter.split_documents(documents)
    return chunks