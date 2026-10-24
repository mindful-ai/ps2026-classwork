# Transformer Architecture – Workshop Handout

## Overview

A Transformer is a neural network architecture that processes sequences using **attention mechanisms** instead of recurrence. It is the foundation of modern Large Language Models (LLMs) such as GPT, Llama, Gemma, and Mistral.

---

# 1. Input Embedding

## Purpose
Convert words/tokens into numerical vectors that the model can process.

## Key Points
- LLMs do not understand raw text.
- Each token is mapped to a high-dimensional vector.
- Similar words tend to have similar embeddings.
- Typical dimensions: 768, 1024, 4096, etc.

---

# 2. Positional Encoding

## Purpose
Tell the model the order of words.

## Why Needed?
Self-attention processes all tokens simultaneously and has no natural notion of sequence.

## Key Points
- Adds position information to embeddings.
- Distinguishes between different word orders.
- Modern LLMs often use Rotary Positional Embeddings (RoPE).

---

# 3. Self-Attention

## Purpose
Determine which words should pay attention to which other words.

## Key Points
- Captures relationships between tokens.
- Enables long-range dependencies.
- Allows contextual understanding.

### Internal Components

#### Query (Q)
What am I looking for?

#### Key (K)
What information do I contain?

#### Value (V)
What information should I pass forward?

### Attention Formula

Attention(Q,K,V) = softmax(QKᵀ/√d)V

---

# 4. Multi-Head Attention

## Purpose
Learn multiple relationships simultaneously.

## Key Points
- Multiple attention heads run in parallel.
- Different heads learn different patterns.
- Outputs are concatenated and combined.
- Improves representation quality.

Examples:
- Grammar relationships
- Subject–verb relationships
- Long-distance references

---

# 5. Attention Mask

## Purpose
Prevent looking at future tokens during generation.

## Key Points
- Essential for autoregressive generation.
- Creates causal behavior.
- Ensures the model predicts one token at a time.

---

# 6. Residual Connections and Layer Normalization

## Purpose
Stabilize training and improve gradient flow.

## Residual Connection

Output = Input + LayerOutput

## Benefits
- Prevents vanishing gradients.
- Enables deep networks.
- Preserves information flow.

## Layer Normalization
- Normalizes activations.
- Improves convergence.
- Stabilizes training.

---

# 7. Feed Forward Network (FFN)

## Purpose
Perform deeper processing after attention.

## Structure

Linear → Activation (GELU/ReLU) → Linear

## Key Points
- Applied independently to every token.
- Usually contains most of the model parameters.
- Learns complex transformations.

### Simple Analogy
- Attention = Gather information
- FFN = Process information

---

# 8. Encoder Layer

## Purpose
Build contextual understanding.

## Components
- Multi-head attention
- Add & Norm
- Feed Forward Network
- Add & Norm

## Common Models
- BERT
- RoBERTa
- Sentence Transformers

## Applications
- Classification
- Semantic Search
- Embeddings

---

# 9. Decoder Layer

## Purpose
Generate text.

## Components
- Masked self-attention
- Add & Norm
- Feed Forward Network
- Add & Norm

## Common Models
- GPT
- Llama
- Gemma
- Mistral

## Applications
- Chatbots
- Text Generation
- Code Generation

---

# 10. Cross-Attention

## Purpose
Allow the decoder to use encoder outputs.

## Common Applications
- Translation
- Summarization
- Sequence-to-sequence tasks

---

# 11. Transformer Block

## Purpose
Basic building unit of the Transformer.

## Typical GPT Block

1. Masked Self-Attention
2. Add & Norm
3. Feed Forward Network
4. Add & Norm

## Key Point
A Transformer is simply many such blocks stacked together.

---

# 12. Stacked Layers

## Purpose
Learn increasingly abstract representations.

### Typical Progression
- Early Layers → Words and syntax
- Middle Layers → Grammar and semantics
- Deep Layers → Concepts and reasoning patterns

---

# 13. Output Projection Layer

## Purpose
Convert hidden representations into vocabulary scores.

## Process

Hidden State → Linear Projection → Vocabulary Scores

---

# 14. Softmax

## Purpose
Convert scores into probabilities.

## Example

- cat → 0.72
- dog → 0.15
- bird → 0.07

---

# 15. Token Sampling

## Purpose
Choose the next token.

## Common Methods
- Greedy Search
- Beam Search
- Top-K Sampling
- Top-P Sampling
- Temperature Sampling

## Impact
Controls:
- Creativity
- Determinism
- Diversity

---

# One-Page Summary

| Component | Purpose |
|------------|----------|
| Embedding | Convert tokens to vectors |
| Positional Encoding | Preserve word order |
| Self-Attention | Learn relationships between tokens |
| Multi-Head Attention | Learn multiple relationships simultaneously |
| Attention Mask | Prevent looking ahead |
| Layer Normalization | Stabilize training |
| Residual Connection | Preserve information flow |
| Feed Forward Network | Deep processing and reasoning |
| Encoder | Understanding text |
| Decoder | Generating text |
| Cross-Attention | Connect encoder and decoder |
| Transformer Block | Basic building unit |
| Stacked Layers | Hierarchical learning |
| Output Projection | Produce vocabulary scores |
| Softmax | Convert scores to probabilities |
| Sampling | Choose next token |

---

# Workshop Analogy

- Embedding → Convert words into a language the computer understands.
- Positional Encoding → Number the seats in a classroom.
- Attention → Students looking at relevant classmates before answering.
- Multi-Head Attention → Multiple groups focusing on different aspects.
- FFN → Individual thinking after gathering information.
- Transformer Blocks → Multiple rounds of discussion and reasoning.
- Output Layer → Final answer spoken aloud.

---

# Key Takeaway

The Transformer repeatedly performs two operations:

1. Gather information using Attention.
2. Process information using Feed Forward Networks.

Stacking many such layers enables modern LLMs to understand context, reason over information, and generate human-like text.
