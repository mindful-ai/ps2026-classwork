# CIS Windows 11 RAG Workshop

A notebook-first, step-by-step workshop for implementing and comparing RAG architectures using the CIS Windows 11 Benchmark.

## Setup

1. Create and activate a Python virtual environment.
2. Install Jupyter if needed.
3. Open `notebooks/00_environment_setup.ipynb`.
4. Review the configuration and set `RUN_INSTALL = True` in the installation cell when ready.
5. Restart the kernel after installing dependencies.
6. Place your authorized CIS Windows 11 Benchmark PDF in `data/benchmark/`.
7. Run the optional Ollama and embedding smoke tests when appropriate.

Example Windows PowerShell commands from the project root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install jupyter
jupyter lab
```

Then open `notebooks/00_environment_setup.ipynb`.

## Model configuration

The setup notebook defaults to Ollama with `gemma4:e2b` for chat and `sentence-transformers/all-MiniLM-L6-v2` for embeddings. These are configurable examples, not hard requirements. Make sure the selected Ollama model is installed locally before enabling its smoke test.

## Workshop notebooks

- `00_environment_setup.ipynb` — environment and dependency checks
- `01_naive_rag.ipynb` — planned next
- `02_advanced_rag.ipynb` through `11_multimodal_rag.ipynb` — added as we implement each architecture

## Safety and evidence

The CIS Benchmark documents recommended settings; it does not prove that a specific computer complies. Compliance assessment requires trusted machine configuration or audit evidence. Do not commit sensitive evidence or credentials to version control.
