# Key Execution Details

## The First Run

`pipeline()` automatically detects whether the model files already exist on your computer.

- If the model is **not** available locally, it downloads the following from the Hugging Face Hub:
  - Model weights
  - Tokenizer
  - Configuration files

## Subsequent Runs

On future executions, the Transformers library checks your local cache first.

- If the model is found in the cache, it skips the network download entirely.
- The model is loaded directly from local storage, resulting in much faster startup.

## Cache Location

By default, downloaded model files are stored in the following directory:

```text
~/.cache/huggingface/hub
```

## Hardware Execution

By default, the pipeline runs on the **CPU**.

To use hardware acceleration, specify the `device` parameter:

- **NVIDIA GPU (CUDA):**

  ```python
  pipeline(..., device=0)
  ```

- **Apple Silicon (MPS):**

  ```python
  pipeline(..., device="mps")
  ```