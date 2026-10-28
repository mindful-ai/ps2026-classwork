# pip install -U \
#     langchain \
#     langchain-community \
#     langchain-text-splitters \
#     langchain-huggingface \
#     langchain-chroma \
#     sentence-transformers \
#     docx2txt

from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# ============================================================
# CONFIG
# ============================================================

DOC_PATH = "medical_knowledge_dataset.docx"

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "medical_docs"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ============================================================
# 1. LOAD DOCUMENT
# ============================================================

print("\n=== Loading document ===")

loader = Docx2txtLoader(DOC_PATH)

documents = loader.load()

print(f"Documents loaded: {len(documents)}")


# ============================================================
# 2. FILTER DOCUMENTS
# ============================================================

MIN_CHAR_LENGTH = 50

documents = [
    doc
    for doc in documents
    if len(doc.page_content.strip()) >= MIN_CHAR_LENGTH
]

print(f"Documents after filtering: {len(documents)}")


# ============================================================
# 3. SPLIT DOCUMENTS
# ============================================================

print("\n=== Splitting documents ===")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]
)

chunks = text_splitter.split_documents(documents)

print(f"Total chunks created: {len(chunks)}")


# ============================================================
# 4. ADD METADATA
# ============================================================

for i, chunk in enumerate(chunks):

    chunk.metadata["source"] = DOC_PATH
    chunk.metadata["chunk_id"] = i


# ============================================================
# 5. CREATE EMBEDDING MODEL
# ============================================================

print("\n=== Loading embedding model ===")

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL,
    model_kwargs={
        "device": "cpu"
    },
    encode_kwargs={
        "normalize_embeddings": True
    }
)


# ============================================================
# 6. CREATE / LOAD CHROMA VECTOR STORE
# ============================================================

print("\n=== Creating Chroma vector store ===")

vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_PATH
)


# ============================================================
# 7. AVOID DUPLICATE INGESTION
# ============================================================

existing_count = vectorstore._collection.count()

print(f"Existing vectors: {existing_count}")

if existing_count > 0:

    print(
        "\n⚠️ Chroma collection already contains data."
    )

    print(
        f"Existing document count: {existing_count}"
    )

    print("Skipping ingestion.")

    exit()


# ============================================================
# 8. ADD DOCUMENTS TO CHROMA
# ============================================================

print("\n=== Adding documents to Chroma ===")

BATCH_SIZE = 500

for i in range(0, len(chunks), BATCH_SIZE):

    batch = chunks[i:i + BATCH_SIZE]

    vectorstore.add_documents(
        documents=batch
    )

    print(
        f"Embedded and stored: "
        f"{i} → {min(i + BATCH_SIZE, len(chunks))}"
    )


# ============================================================
# 9. FINAL STATUS
# ============================================================

final_count = vectorstore._collection.count()

print("\n===================================")
print("✅ INGESTION COMPLETE")
print("===================================")

print(f"Chunks created : {len(chunks)}")
print(f"Vectors stored : {final_count}")
print(f"Chroma path    : {CHROMA_PATH}")
print(f"Collection     : {COLLECTION_NAME}")