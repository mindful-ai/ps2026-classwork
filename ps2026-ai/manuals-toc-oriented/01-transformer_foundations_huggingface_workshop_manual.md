# Workshop Manual: Transformer Foundations, Hugging Face and Efficient Model Adaptation

*Hands-on workshop handout · NLP and Transformer models · Beginner to intermediate*

## 1. Workshop overview

This workshop takes learners from understanding the fundamentals of Transformer models to using pre-trained models, generating embeddings, evaluating semantic retrieval, choosing adaptation strategies, and measuring inference efficiency.

The emphasis is on **using and adapting existing foundation models**, rather than training a foundation model from scratch.

### Learning objectives

By the end of the workshop, participants should be able to:

- Explain tokens, embeddings, self-attention, positional information, and encoder/decoder architectures.
- Distinguish pre-training, fine-tuning, and instruction tuning.
- Load pre-trained models and tokenizers using Hugging Face Transformers.
- Perform batched text classification and information extraction.
- Generate sentence embeddings and evaluate cosine similarity and nearest-neighbour retrieval.
- Compare prompting, feature extraction, and parameter-efficient fine-tuning (PEFT).
- Measure latency, memory usage, and the impact of batch size.
- Explain quantization and make informed model-size and deployment trade-offs.

## 2. Recommended learning sequence

1. **Transformer foundations:** Tokens → Embeddings → Self-attention → Positional information → Architecture patterns
2. **Pre-trained model workflow:** Pre-training → Fine-tuning → Instruction tuning → Inference
3. **Hugging Face practice:** Model and tokenizer loading → Classification → Extraction → Batched inference
4. **Embeddings and similarity:** Sentence embeddings → Cosine similarity → Nearest neighbours → Retrieval evaluation
5. **Efficient adaptation and inference:** Prompting → Feature extraction → PEFT → Benchmarking → Quantization

---

## 3. Module 1 — Transformer foundations

### 3.1 Tokens and tokenization

A Transformer does not directly process raw text. A tokenizer converts text into smaller units called *tokens*, which are mapped to numerical token IDs.

Example:

```text
Input text: "Transformers understand language"

Tokenization: ["Transformers", "understand", "language"]

Token IDs: [101, 2487, 2653]  # Illustrative only
```

Actual tokens and IDs depend on the tokenizer. A token can be a whole word, part of a word, punctuation, or another text unit.

**Key concepts**

- Vocabulary and token IDs
- Subword tokenization
- Special tokens such as beginning-of-sequence and end-of-sequence markers
- Padding and truncation
- Attention masks

**Hands-on activity:** Load a tokenizer, inspect tokens and token IDs, and compare how it tokenizes short and long sentences.

### 3.2 Embeddings

Token IDs are discrete identifiers, not meaningful numerical representations by themselves. An embedding layer maps each token ID to a dense vector.

For example, a token might be represented by a vector with hundreds of numerical dimensions. The model learns these representations during training.

Distinguish two concepts:

- **Token embeddings:** Initial vector representations of individual tokens.
- **Contextual hidden representations:** Vectors produced by Transformer layers that incorporate contextual information.

The representation of a word can change depending on its surrounding text.

### 3.3 Self-attention

Self-attention allows each token to use information from other relevant tokens in its context.

For each input representation, the attention mechanism derives queries (Q), keys (K), and values (V). Scaled dot-product attention is:

\[
\operatorname{Attention}(Q,K,V)
=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V
\]

Where:

- \(QK^\top\) calculates compatibility scores between tokens.
- \(\sqrt{d_k}\) scales the scores.
- Softmax converts scores into attention weights.
- Multiplying by \(V\) combines information from the tokens.

*Illustrative example:* “The animal didn't cross the road because it was tired.” Self-attention can help the model relate “it” to “the animal” using surrounding context. This is an illustration of the mechanism, not a guarantee that the model will resolve every reference correctly.

**Topics to cover**

- Query, key, and value projections
- Attention scores and attention masks
- Multi-head attention
- Residual connections and layer normalization
- Feed-forward networks within Transformer blocks

### 3.4 Positional information

Self-attention alone does not inherently encode token order. Transformer architectures introduce positional information so the model can distinguish sequences with different arrangements.

Cover:

- Absolute positional embeddings
- Relative positional representations
- Rotary positional embeddings (RoPE)
- Context length and its practical limitations

Learners should understand that positional methods differ across model families and are not all implemented in the same way.

### 3.5 Encoder, decoder and encoder-decoder architectures

#### Encoder-only

**Flow:** Input tokens → Bidirectional self-attention → Contextual representations

Typical use: classification, token classification and feature extraction. Example family: BERT.

#### Decoder-only

**Flow:** Prompt and previous tokens → Causal self-attention → Next-token prediction

Typical use: text generation and conversational applications. Example family: GPT-style models.

#### Encoder-decoder

**Flow:** Input → Encoder → Decoder with cross-attention → Generated output sequence

Typical use: translation, summarization and sequence-to-sequence tasks. Example family: T5.

**Practical takeaway:** Architecture influences which model and inference method are suitable for a task. An encoder model is not automatically a text generator, and a decoder-only model does not automatically provide high-quality sentence embeddings.

---

## 4. Module 2 — Pre-trained model workflow

### 4.1 Pre-training

Pre-training learns general-purpose representations or language capabilities from large training datasets.

Common objectives include:

- **Masked language modeling:** Predict masked tokens using context.
- **Causal language modeling:** Predict the next token based on preceding tokens.
- **Sequence-to-sequence objectives:** Learn to generate target sequences from input sequences.

Training foundation models from scratch is outside the scope of this workshop because it requires substantial data, compute, infrastructure, and evaluation.

### 4.2 Fine-tuning

Fine-tuning continues training an existing model on a task-specific dataset.

Examples:

- Classifying customer complaints
- Extracting fields from business documents
- Categorizing technical support tickets

Fine-tuning can improve task performance, but results depend on data quality, dataset size, model selection and evaluation.

### 4.3 Instruction tuning

Instruction tuning trains a model on examples of instructions and desired responses so it can better follow user requests.

It is distinct from general pre-training and from task-specific fine-tuning, although instruction tuning itself is a form of fine-tuning.

### 4.4 Inference without foundation-model training

Inference means using a trained model to generate predictions or outputs.

A normal inference workflow is:

1. Select a model suited to the task.
2. Load the model and tokenizer.
3. Prepare the input.
4. Run the model.
5. Decode or interpret the output.
6. Evaluate quality, latency and resource use.

The workshop will use pre-trained models and inference pipelines. Fine-tuning and PEFT will be introduced as adaptation options, without requiring learners to train a large foundation model.

### 4.5 Model selection exercise

| Requirement | Suitable starting point |
|---|---|
| Classify text into predefined labels | Pre-trained sequence-classification model |
| Extract named entities | Token-classification model |
| Generate conversational text | Instruction-tuned causal language model |
| Find semantically similar sentences | Sentence-embedding model |
| Summarize or translate text | Suitable sequence-to-sequence model or instruction-tuned LLM |

**Exercise:** For each of five sample business requirements, select a model type and explain why it fits.

---

## 5. Module 3 — Hugging Face practice

### 5.1 Environment setup

Use a Python virtual environment.

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\\Scripts\\Activate.ps1
```

Install the core libraries:

```bash
python -m pip install --upgrade pip
pip install transformers torch sentence-transformers scikit-learn
```

For GPU execution, install a PyTorch build compatible with the machine's hardware and drivers. The workshop can also run on CPU using small models, though inference may be slower.

### 5.2 Load a pre-trained model and tokenizer

For a simple first demonstration, use a text-classification pipeline.

```python
from transformers import pipeline

classifier = pipeline(
    task="sentiment-analysis",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english"
)

texts = [
    "The training was excellent.",
    "The application is slow and frustrating.",
    "The documentation is clear and useful."
]

results = classifier(texts)

for text, result in zip(texts, results):
    print(text)
    print(result)
```

Discuss:

- Model identifiers and model repositories
- Automatic tokenizer loading
- Labels and confidence scores
- Model download and local caching
- The distinction between a classification score and a calibrated probability

The model above is a sentiment classifier, not a general-purpose chatbot.

### 5.3 Inspect tokenization explicitly

```python
from transformers import AutoTokenizer

model_id = (
    "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
)

tokenizer = AutoTokenizer.from_pretrained(model_id)

text = "Transformers process tokens in context."

encoded = tokenizer(
    text,
    return_tensors="pt",
    truncation=True
)

print("Token IDs:", encoded["input_ids"])
print("Attention mask:", encoded["attention_mask"])
print("Tokens:", tokenizer.convert_ids_to_tokens(
    encoded["input_ids"][0]
))
```

Ask learners to identify the input IDs, padding behavior, and attention mask.

### 5.4 Batched inference

Batched inference processes several examples in a single call. This often improves throughput, although the ideal batch size depends on the hardware, model, sequence lengths and memory constraints.

```python
from transformers import pipeline

classifier = pipeline(
    "sentiment-analysis",
    model=(
        "distilbert/"
        "distilbert-base-uncased-finetuned-sst-2-english"
    )
)

texts = [
    "The service was quick.",
    "My order arrived damaged.",
    "The support team solved the issue.",
    "The refund process was disappointing."
]

batch_size = 2

for start in range(0, len(texts), batch_size):
    batch = texts[start:start + batch_size]
    results = classifier(batch, batch_size=batch_size)

    for text, result in zip(batch, results):
        print(text, "=>", result)
```

The loop demonstrates application-level batching. For large datasets, use a streaming or dataset-based approach to avoid keeping all inputs and outputs in memory.

### 5.5 Information extraction

Named-entity recognition (NER) identifies entities such as people, organizations and locations.

```python
from transformers import pipeline

extractor = pipeline(
    "token-classification",
    model="dslim/bert-base-NER",
    aggregation_strategy="simple"
)

text = (
    "Anil works at Microsoft in Bengaluru "
    "and attended a conference in Singapore."
)

entities = extractor(text)

for entity in entities:
    print(
        entity["word"],
        entity["entity_group"],
        round(entity["score"], 3)
    )
```

Discuss entity labels, token aggregation, confidence scores and model limitations. NER does not automatically extract every business field; structured document extraction may need task-specific models, rules or an LLM.

### Module 3 lab checklist

- [ ] Load a model and tokenizer.
- [ ] Inspect token IDs and attention masks.
- [ ] Classify at least ten text samples.
- [ ] Compare single-example and batched inference.
- [ ] Extract entities from a sample paragraph.
- [ ] Record errors and examples of incorrect predictions.

---

## 6. Module 4 — Embeddings and similarity

### 6.1 Generate sentence embeddings

Sentence embeddings represent entire sentences or passages as dense vectors. They are commonly used in semantic search, clustering, duplicate detection and retrieval-augmented generation (RAG).

For this lab, use the `sentence-transformers` library.

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

sentences = [
    "How do I reset my password?",
    "I forgot my account password.",
    "How can I bake sourdough bread?",
    "I cannot log in to my account."
]

embeddings = model.encode(
    sentences,
    normalize_embeddings=True
)

print("Number of sentences:", len(sentences))
print("Embedding matrix shape:", embeddings.shape)
```

For this model, each sentence embedding has 384 dimensions.

Explain:

- Embedding dimension
- Sentence-level versus token-level embeddings
- Similarity-oriented training
- Normalization
- Model suitability for the language, domain and task

### 6.2 Calculate cosine similarity

Cosine similarity compares the directions of two vectors. It is frequently used to assess semantic similarity.

\[
\operatorname{cosine}(A,B)=
\frac{A\cdot B}{\lVert A\rVert\lVert B\rVert}
\]

When vectors are L2-normalized, cosine similarity is equal to their dot product.

**Interpretation:** A higher score indicates greater alignment between vectors. It is not automatically a percentage of semantic equivalence, and the appropriate threshold depends on the model and task.

```python
from sklearn.metrics.pairwise import cosine_similarity

similarity_matrix = cosine_similarity(embeddings)

for i in range(len(sentences)):
    for j in range(i + 1, len(sentences)):
        print(
            round(similarity_matrix[i, j], 3),
            "|",
            sentences[i],
            "<->",
            sentences[j]
        )
```

**Exercise:** Identify which sentence is most similar to “How do I reset my password?” and explain why keyword matching alone may miss some relevant results.

### 6.3 Nearest-neighbour retrieval

Suppose the application stores a set of support documents. Given a query, it retrieves the documents with the most similar embeddings.

```python
import numpy as np

documents = [
    "Reset your password from account settings.",
    "Refunds are processed within five business days.",
    "Use two-factor authentication to secure your account.",
    "Contact support if you cannot access your account."
]

document_embeddings = model.encode(
    documents,
    normalize_embeddings=True
)

query = "I cannot sign in to my account"
query_embedding = model.encode(
    [query],
    normalize_embeddings=True
)

scores = (
    query_embedding @ document_embeddings.T
).flatten()

top_k = 2
nearest = np.argsort(scores)[::-1][:top_k]

for index in nearest:
    print(
        f"{scores[index]:.3f} | {documents[index]}"
    )
```

This is a basic exact-search implementation. Vector databases and approximate nearest-neighbour indexes become useful when the corpus is large.

### 6.4 Evaluate retrieval quality

A retrieval system should be evaluated against known relevant documents, not merely judged by whether the top results look reasonable.

Key metrics:

| Metric | What it measures |
|---|---|
| Precision@k | Fraction of the top-k results that are relevant |
| Recall@k | Fraction of all relevant documents retrieved in the top k |
| MRR | How highly the first relevant result ranks |
| nDCG@k | Ranking quality when relevance has multiple grades |

For example, if two of the top five documents are relevant, then Precision@5 is \(2/5 = 0.4\).

**Practical lab**

1. Create a corpus of 20–50 short documents.
2. Prepare at least ten realistic search queries.
3. Label the relevant documents for each query.
4. Run nearest-neighbour retrieval.
5. Calculate Precision@k and Recall@k.
6. Examine missed relevant documents and irrelevant matches.
7. Discuss how embedding model choice, chunking, metadata filters and reranking could improve results.

The central lesson is that **embedding similarity and retrieval quality are related, but they are not the same thing**.

---

## 7. Module 5 — Efficient adaptation and inference

### 7.1 Compare adaptation choices

Different adaptation methods solve different problems. Begin with the cheapest and simplest approach before introducing additional training.

| Approach | What changes? | Best suited for |
|---|---|---|
| Prompting | Instructions and input examples | Quick experiments and flexible tasks |
| Feature extraction | A fixed model produces features for a downstream task | Small datasets and conventional classifiers |
| Full fine-tuning | Most or all model parameters | Tasks with sufficient data and compute |
| PEFT | A small subset of trainable parameters or added modules | Lower-cost adaptation of supported models |

### 7.2 Prompting

Prompting changes the input instructions rather than model weights.

Example:

```text
Classify the support ticket into exactly one category:
BILLING, TECHNICAL, ACCOUNT, OTHER.

Ticket:
"I was charged twice for the same order."

Return only the category.
```

Advantages:

- Fast to experiment with
- No training pipeline required
- Easy to change task instructions

Limitations:

- Output consistency may vary
- Quality depends on the model and prompt
- Repeated inference can be expensive at scale
- Structured outputs still require validation

For a hosted API model, also consider token costs, rate limits, privacy and network latency.

### 7.3 Feature extraction

In feature extraction, a pre-trained model generates representations that are then used by another model, such as logistic regression.

A common text-classification workflow is:

1. Generate sentence embeddings.
2. Create labeled training and validation datasets.
3. Train a lightweight classifier on the embeddings.
4. Evaluate against a held-out test set.
5. Compare performance with prompting or a fine-tuned model.

This is particularly useful when labeled data is limited and the pre-trained embedding model already represents the task reasonably well.

### 7.4 Parameter-efficient fine-tuning

PEFT adapts a model while updating fewer parameters than full fine-tuning.

Important concepts:

- **LoRA:** Learns low-rank updates to selected weight matrices.
- **Adapters:** Adds small trainable modules to a mostly frozen model.
- **Soft prompts:** Learns trainable prompt representations for supported methods.

With LoRA, the original model weights are generally kept frozen while low-rank update parameters are trained. This can reduce trainable parameter count and optimizer-state memory, though total memory use still depends on the base model, precision, sequence length and training setup.

PEFT is not automatically the best choice. It still requires suitable data, evaluation, training infrastructure and compatibility with the chosen architecture.

### 7.5 Choose an adaptation strategy

Use the following decision guide:

1. **Start with a baseline.** Use an existing pre-trained model or prompt. Establish quality and cost before adapting it.
2. **Check performance.** If it is sufficient, keep the simpler solution and validate it on representative data. If not, identify whether the problem is instructions, representation quality, or model capability.
3. **Choose the next step.**
   - **Prompting:** Choose when instructions, examples or output formatting are the main issues.
   - **Feature extraction:** Choose when a lightweight supervised classifier can learn from existing representations.
   - **PEFT or full fine-tuning:** Consider when a suitable labeled dataset exists and simpler approaches do not meet quality requirements.

Before selecting a method, compare expected quality, labeled-data availability, training cost, inference cost, latency, privacy, operational complexity and risk of regressions.

### 7.6 Measure inference latency and throughput

Performance should be measured, not guessed.

Important measurements:

- **Latency:** Time taken to produce a result.
- **Throughput:** Number of examples processed per unit of time.
- **Peak memory:** Maximum memory consumed during execution.
- **Batch-size effects:** How batching changes throughput, latency and memory.
- **Sequence-length effects:** How longer inputs affect computation and memory.

A simple CPU-compatible benchmarking example:

```python
import time
import statistics
from transformers import pipeline

model_id = (
    "distilbert/"
    "distilbert-base-uncased-finetuned-sst-2-english"
)

classifier = pipeline(
    "sentiment-analysis",
    model=model_id,
    device=-1
)

texts = [
    "The service was excellent.",
    "The application failed to load.",
    "The issue has been resolved.",
    "I am unhappy with the response."
] * 8

batch_size = 8
latencies = []

# Warm-up
classifier(texts[:batch_size], batch_size=batch_size)

for start in range(0, len(texts), batch_size):
    batch = texts[start:start + batch_size]

    t0 = time.perf_counter()
    classifier(batch, batch_size=batch_size)
    elapsed = time.perf_counter() - t0

    latencies.append(elapsed)

total_time = sum(latencies)
throughput = len(texts) / total_time

print("Total examples:", len(texts))
print("Total time (s):", round(total_time, 3))
print("Mean batch latency (s):", round(statistics.mean(latencies), 4))
print("Throughput (examples/s):", round(throughput, 2))
```

This measures batch-processing time, not individual request latency or production-grade p95/p99 latency. For a fair benchmark, repeat runs, compare multiple batch sizes, control hardware and input lengths, and report variability. For GPU measurements, synchronize the GPU around timed regions and record peak allocated GPU memory. CPU and GPU measurements should not be directly compared without accounting for hardware and workload differences.

### 7.7 Quantization and smaller-model trade-offs

Quantization represents model weights or other numerical values using lower precision, often reducing memory requirements and sometimes improving inference speed.

Common precision formats include:

- **FP32:** 32-bit floating point
- **FP16 and BF16:** 16-bit floating point
- **INT8:** 8-bit integer quantization
- **4-bit weight quantization:** Further reduction in weight storage

| Consideration | Potential benefit | Possible cost |
|---|---|---|
| Lower precision | Reduced weight memory | Quality degradation in some tasks |
| Smaller model | Faster inference and lower resource needs | Reduced capability on complex tasks |
| Larger batch | Better throughput | Higher memory use and possible latency increase |
| Longer context | More input information | Greater compute and memory requirements |

Quantization does not guarantee faster inference: the actual result depends on hardware support, kernels, quantization method and model architecture.

**Hands-on experiment:** Compare two suitable model sizes, or compare two supported precision settings for the same model. Measure task quality, latency, throughput and peak memory. Record whether the resource savings justify any quality loss.

---

## 8. Capstone exercise — Build a small semantic support assistant

**Scenario:** A company wants to help employees find answers from a collection of support documents.

### Implementation steps

1. **Prepare the corpus.** Create 30–50 short documents about account access, technical issues, billing, and support policies.
2. **Build the retrieval system.** Generate sentence embeddings, store them in a matrix, and retrieve the top-k documents using cosine similarity.
3. **Evaluate retrieval.** Prepare sample queries with relevance labels and calculate Precision@k and Recall@k.
4. **Add a classifier.** Use a pre-trained text-classification model to classify incoming support tickets.
5. **Benchmark inference.** Compare batch sizes and measure latency and throughput.
6. **Recommend an optimization.** Explain whether prompting, feature extraction, PEFT, quantization, or a smaller model is most appropriate for the scenario.

### Expected deliverables

- Working Python implementation
- Retrieval evaluation results
- Classification output for sample tickets
- Benchmark results in a CSV or table
- A short model-selection and optimization report

---

## 9. Quick reference: tools and libraries

| Tool | Purpose in the workshop |
|---|---|
| `transformers` | Load pre-trained models, tokenizers and inference pipelines |
| `torch` | Tensor operations and model execution |
| `sentence-transformers` | Generate sentence embeddings |
| `scikit-learn` | Cosine similarity, evaluation metrics and lightweight classifiers |
| `time` | Measure elapsed execution time |
| `statistics` | Summarize benchmark results |
| `psutil` *(optional)* | Inspect CPU and process memory |
| `nvidia-smi` *(optional)* | Inspect NVIDIA GPU utilization and memory |

For further reference, use the official documentation:

- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [Sentence Transformers](https://huggingface.co/docs/sentence-transformers/)
- [Parameter-Efficient Fine-Tuning (PEFT)](https://huggingface.co/docs/peft/)
- [Scikit-learn](https://scikit-learn.org/stable/)

---

## 10. Final learning outcomes checklist

Participants should be able to explain or demonstrate each of the following:

- [ ] Explain how tokenization, embeddings and self-attention work together.
- [ ] Distinguish encoder-only, decoder-only and encoder-decoder architectures.
- [ ] Explain pre-training, fine-tuning and instruction tuning.
- [ ] Load and run a pre-trained model with Hugging Face.
- [ ] Perform batched classification and named-entity extraction.
- [ ] Generate sentence embeddings and retrieve nearest neighbours.
- [ ] Evaluate retrieval quality using labeled examples.
- [ ] Compare prompting, feature extraction and PEFT.
- [ ] Measure latency, throughput and memory usage.
- [ ] Explain quantization and select a model based on quality, cost and deployment constraints.

**Workshop principle:** Start with a pre-trained model, establish a measurable baseline, evaluate it on representative data, and introduce adaptation or optimization only when the evidence justifies it.
