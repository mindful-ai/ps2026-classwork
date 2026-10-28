# pip install -U \
#     langchain \
#     langchain-chroma \
#     langchain-huggingface \
#     langchain-groq \
#     sentence-transformers


from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


# ============================================================
# CONFIG
# ============================================================

CHROMA_PATH = "./chroma_db"

COLLECTION_NAME = "medical_docs"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

MODEL = "openai/gpt-oss-20b"

TOP_K = 5


# ============================================================
# LOAD GROQ API KEY
# ============================================================

groq_path = (
    r"E:\Lenovo Ideapad 330\company-material"
    r"\digital-workforce-transformation"
    r"\ai-upskill-12\key-vault\groq\api.key"
)

with open(groq_path, "r") as f:
    api_key = f.read().strip()


# ============================================================
# EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

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
# LOAD CHROMA
# ============================================================

print("Loading Chroma vector store...")

vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=CHROMA_PATH
)


# ============================================================
# CREATE RETRIEVER
# ============================================================

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": TOP_K
    }
)


# ============================================================
# LLM
# ============================================================

llm = ChatGroq(
    api_key=api_key,
    model=MODEL,
    temperature=0.3,
    max_tokens=1000
)


# ============================================================
# PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are a medical assistant.

Use the provided context to answer the question.

If the context contains relevant information, including partial
information, use it to formulate the answer.

If the context is completely unrelated to the question, say:
"I don't know."

Do not invent information that is not supported by the context.

Give a concise answer using bullet points.
"""


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            SYSTEM_PROMPT
        ),
        (
            "human",
            """
Context:
{context}

Question:
{question}

Answer:
"""
        )
    ]
)


# ============================================================
# FORMAT RETRIEVED DOCUMENTS
# ============================================================

def format_docs(docs):
    return "\n\n".join(
        doc.page_content
        for doc in docs
    )


# ============================================================
# RAG CHAIN
# ============================================================

rag_chain = (
    {
        "context": retriever | format_docs,
        "question": lambda x: x
    }
    | prompt
    | llm
    | StrOutputParser()
)


# ============================================================
# ASK
# ============================================================

def ask(question):

    try:

        answer = rag_chain.invoke(question)

        return {
            "answer": answer
        }

    except Exception as e:

        return {
            "error": str(e)
        }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    question = "What is diabetes?"

    result = ask(question)

    print("\n==============================")
    print("QUESTION")
    print("==============================")
    print(question)

    print("\n==============================")
    print("ANSWER")
    print("==============================")
    print(result)