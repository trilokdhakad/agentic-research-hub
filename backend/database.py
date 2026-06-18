from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

persist_directory = "./chroma_db"


def get_vector_store():
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )


def add_documents_to_db(chunks):
    vector_store = get_vector_store()
    vector_store.add_documents(chunks)
    return True


def get_all_documents():
    vector_store = get_vector_store()

    data = vector_store.get()

    if not data or "metadatas" not in data:
        return []

    document_info = {}

    for metadata in data["metadatas"]:
        if not metadata:
            continue

        source = metadata.get("source")

        if not source:
            continue

        if source not in document_info:
            extension = source.split(".")[-1].lower()

            document_info[source] = {
                "name": source,
                "chunks": 0,
                "type": extension
            }

        document_info[source]["chunks"] += 1

    return sorted(
        document_info.values(),
        key=lambda x: x["name"].lower()
    )


def delete_document(filename):
    vector_store = get_vector_store()

    data = vector_store.get()

    ids_to_delete = []

    for idx, metadata in enumerate(data["metadatas"]):
        if metadata.get("source") == filename:
            ids_to_delete.append(data["ids"][idx])

    if ids_to_delete:
        vector_store.delete(ids=ids_to_delete)

    return len(ids_to_delete)


def document_exists(filename):
    vector_store = get_vector_store()

    data = vector_store.get()

    for metadata in data["metadatas"]:
        if metadata.get("source") == filename:
            return True

    return False