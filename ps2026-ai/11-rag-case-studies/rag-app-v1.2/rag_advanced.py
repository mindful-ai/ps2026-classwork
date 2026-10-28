# ============================================================
# RAG WITH RRRGV
#
# LangChain upgraded version
#
# Pipeline:
#
# Question
#    ↓
# Query Rewriting
#    ↓
# Chroma Retriever
#    ↓
# Cross Encoder Reranking
#    ↓
# Contextual Compression
#    ↓
# LLMChainExtractor
#    ↓
# RAG Generation
#    ↓
# Validation
#
# ============================================================


# ============================================================
# INSTALL
# ============================================================
#
# pip install -U \
#     langchain \
#     langchain-community \
#     langchain-core \
#     langchain-chroma \
#     langchain-huggingface \
#     langchain-groq \
#     sentence-transformers
#
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

import re

from sentence_transformers import CrossEncoder

from langchain_chroma import Chroma

from langchain_huggingface import HuggingFaceEmbeddings

from langchain_groq import ChatGroq

from langchain_core.prompts import ChatPromptTemplate

from langchain_core.output_parsers import StrOutputParser

from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors.chain_extract import LLMChainExtractor

from langchain_core.documents import Document

from langchain_core.retrievers import BaseRetriever


# ============================================================
# CONFIG
# ============================================================

CHROMA_PATH = "./chroma_db"

COLLECTION_NAME = "medical_docs"

MODEL = "openai/gpt-oss-20b"

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

CROSS_ENCODER_MODEL = (
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

RETRIEVAL_K = 10

RERANK_K = 5


# ============================================================
# GROQ API KEY
# ============================================================

groq_path = (
    r"E:\Lenovo Ideapad 330"
    r"\company-material"
    r"\digital-workforce-transformation"
    r"\ai-upskill-12"
    r"\key-vault"
    r"\groq"
    r"\api.key"
)


with open(groq_path, "r") as f:

    api_key = f.read().strip()


# ============================================================
# EMBEDDINGS
# ============================================================

print("\nLoading embedding model...")

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
# CHROMA
# ============================================================

print("Loading Chroma...")

vectorstore = Chroma(

    collection_name=COLLECTION_NAME,

    embedding_function=embeddings,

    persist_directory=CHROMA_PATH
)


# ============================================================
# BASE RETRIEVER
# ============================================================

retriever = vectorstore.as_retriever(

    search_type="similarity",

    search_kwargs={
        "k": RETRIEVAL_K
    }
)


# ============================================================
# LLM
# ============================================================

llm = ChatGroq(

    api_key=api_key,

    model=MODEL,

    temperature=0,

    max_tokens=200
)


# ============================================================
# QUERY REWRITING
# ============================================================

rewrite_prompt = ChatPromptTemplate.from_template(
    """
Rewrite the following question into a concise
search query suitable for semantic document retrieval.

Return ONLY the rewritten query.

Question:
{question}
"""
)


rewrite_chain = (

    rewrite_prompt

    | llm

    | StrOutputParser()
)


def rewrite_query(question):

    return rewrite_chain.invoke(
        {
            "question": question
        }
    ).strip()


# ============================================================
# CROSS ENCODER
# ============================================================

print("Loading cross encoder...")

cross_encoder = CrossEncoder(
    CROSS_ENCODER_MODEL
)


# ============================================================
# CROSS-ENCODER RERANKER
# ============================================================

def rerank_documents(
    query,
    documents,
    top_k=RERANK_K
):

    if not documents:

        return []


    pairs = [

        [
            query,
            doc.page_content
        ]

        for doc in documents
    ]


    scores = cross_encoder.predict(
        pairs
    )


    ranked = sorted(

        zip(documents, scores),

        key=lambda x: x[1],

        reverse=True
    )


    reranked_documents = [

        doc

        for doc, score

        in ranked[:top_k]
    ]


    # Store reranking score
    for doc, score in ranked[:top_k]:

        doc.metadata[
            "rerank_score"
        ] = float(score)


    return reranked_documents


# ============================================================
# CUSTOM RETRIEVER FOR RERANKED DOCUMENTS
# ============================================================
#
# ContextualCompressionRetriever expects a retriever.
#
# Therefore we create a small LangChain-compatible
# retriever that performs:
#
#     Chroma retrieval
#          ↓
#     Cross encoder reranking
#
# ============================================================

class RerankingRetriever(BaseRetriever):

    base_retriever: BaseRetriever
    top_k: int = RERANK_K

    def _get_relevant_documents(
        self,
        query,
        *,
        run_manager=None
    ):

        documents = (
            self.base_retriever.invoke(query)
        )


        return rerank_documents(
            query,
            documents,
            self.top_k
        )


# ============================================================
# RERANKING RETRIEVER
# ============================================================

reranking_retriever = RerankingRetriever(

    base_retriever=retriever,

    top_k=RERANK_K
)


# ============================================================
# LLM CHAIN EXTRACTOR
# ============================================================
#
# This is the contextual compression component.
#
# It receives retrieved documents and extracts only
# the parts relevant to the query.
#
# ============================================================

print("Creating LLMChainExtractor...")

compressor = LLMChainExtractor.from_llm(
    llm
)


# ============================================================
# CONTEXTUAL COMPRESSION RETRIEVER
# ============================================================

compression_retriever = (
    ContextualCompressionRetriever(
        base_retriever=reranking_retriever,
        base_compressor=compressor
    )
)


# ============================================================
# FINAL RAG PROMPT
# ============================================================

rag_prompt = ChatPromptTemplate.from_messages(

    [

        (
            "system",

            """
You are a medical assistant.

Use the provided context to answer the question.

If the context contains relevant information,
including partial information, use it.

Do not invent information that is not supported
by the context.

If the context is completely unrelated,
say:

"I don't know."

Give a concise answer using bullet points.
"""
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
# FINAL RAG CHAIN
# ============================================================

rag_generation_chain = (

    rag_prompt

    | llm

    | StrOutputParser()
)


# ============================================================
# VALIDATION
# ============================================================

validation_prompt = ChatPromptTemplate.from_template(

    """
Score the answer from 0 to 1 based on how correctly
the answer is supported by the provided context.

Return ONLY a number.

Question:
{question}

Context:
{context}

Answer:
{answer}
"""
)


validation_chain = (

    validation_prompt

    | llm

    | StrOutputParser()
)


# ============================================================
# EXTRACT SCORE
# ============================================================

def extract_score(text):

    match = re.search(
        r"\d*\.?\d+",
        text
    )


    if match:

        score = float(
            match.group()
        )

        return min(
            max(score, 0.0),
            1.0
        )


    return 0.0


# ============================================================
# FORMAT DOCUMENTS
# ============================================================

def format_documents(documents):

    return "\n\n".join(

        doc.page_content

        for doc in documents
    )


# ============================================================
# MAIN ASK FUNCTION
# ============================================================

def ask(query):

    # --------------------------------------------------------
    # Check Chroma
    # --------------------------------------------------------

    collection_count = (
        vectorstore._collection.count()
    )


    if collection_count == 0:

        return {

            "error":
            "Chroma DB is empty. "
            "Run ingest.py first."
        }


    print(
        "\n--------------------------------------------------"
    )

    print(
        "\n-- LangChain RAG with RRRGV --\n"
    )


    # ========================================================
    # 1. QUERY REWRITE
    # ========================================================

    rewritten_query = rewrite_query(
        query
    )


    print(
        "🔁 Original Query:",
        query
    )


    print(
        "🔁 Rewritten Query:",
        rewritten_query
    )


    # ========================================================
    # 2. INITIAL RETRIEVAL
    # ========================================================

    initial_docs = retriever.invoke(
        rewritten_query
    )


    print(
        f"\n📚 Documents retrieved: "
        f"{len(initial_docs)}"
    )


    # ========================================================
    # 3. CROSS-ENCODER RERANKING
    # ========================================================

    reranked_docs = rerank_documents(

        rewritten_query,

        initial_docs,

        RERANK_K
    )


    print(
        f"🔀 Documents after reranking: "
        f"{len(reranked_docs)}"
    )


    # ========================================================
    # SHOW RERANKED DOCUMENTS
    # ========================================================

    print("\n🔍 Reranked Documents:")


    for i, doc in enumerate(
        reranked_docs,
        1
    ):

        score = doc.metadata.get(
            "rerank_score",
            0
        )


        print(
            f"{i}. "
            f"score={score:.4f} "
            f"{doc.page_content[:120]}..."
        )


    # ========================================================
    # 4. CONTEXTUAL COMPRESSION
    # ========================================================
    #
    # We invoke the compression retriever.
    #
    # It performs:
    #
    # Reranking
    #     ↓
    # LLMChainExtractor
    #     ↓
    # Relevant passages
    #
    # ========================================================

    compressed_docs = (
        compression_retriever.invoke(
            rewritten_query
        )
    )


    print(
        "\n🗜️ Documents after "
        "contextual compression:",
        len(compressed_docs)
    )


    # ========================================================
    # SHOW COMPRESSED CONTEXT
    # ========================================================

    print(
        "\n📌 Compressed Context:"
    )


    for i, doc in enumerate(
        compressed_docs,
        1
    ):

        print(
            f"\n{i}. "
            f"{doc.page_content}"
        )


    # ========================================================
    # 5. BUILD CONTEXT
    # ========================================================

    context = format_documents(
        compressed_docs
    )


    # ========================================================
    # 6. GENERATE ANSWER
    # ========================================================

    answer = rag_generation_chain.invoke(

        {

            "question": query,

            "context": context
        }
    )


    print(
        "\n💡 Answer:\n",
        answer
    )


    # ========================================================
    # 7. VALIDATE ANSWER
    # ========================================================

    validation_result = (
        validation_chain.invoke(

            {

                "question": query,

                "context": context,

                "answer": answer
            }
        )
    )


    score = extract_score(
        validation_result
    )


    print(
        f"\n✅ Validation Score: "
        f"{score:.2f}"
    )


    print(
        "\n--------------------------------------------------"
    )


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "question": query,

        "rewritten_query":
            rewritten_query,

        "answer":
            answer,

        "validation_score":
            score,

        "retrieved_documents":
            len(initial_docs),

        "reranked_documents":
            len(reranked_docs),

        "compressed_documents":
            len(compressed_docs),

        "context":
            context
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    info = ask(
        "What are the symptoms of diabetes?"
    )


    print(
        "\n\nFINAL RESULT"
    )


    print(
        info["answer"]
    )