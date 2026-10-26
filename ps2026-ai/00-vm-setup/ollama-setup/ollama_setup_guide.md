# Ollama Setup Guide
## Installing Ollama, downloading a model, and running inference with Python

**Audience:** Students and workshop participants  
**Goal:** Install Ollama, run a local large language model (LLM), and call it from a Python program.

---

## 1. What is Ollama?

Ollama is a runtime for downloading and running language models on your own computer. It provides a command-line interface and a local HTTP API that applications such as Python scripts can call.

A typical setup looks like this:

1. **Ollama runtime** manages and runs the model.
2. **LLM** is the model downloaded to the computer.
3. **Python client** sends prompts to Ollama and reads the generated responses.

Inference means using an already-trained model to generate an answer. This exercise does not train or fine-tune a model.

## 2. Check your computer

Before installing:

- Ensure you have a supported, up-to-date version of Windows, macOS, or Linux.
- Ensure you have enough free disk space for the model you intend to download.
- Close unnecessary applications if your laptop has limited RAM.
- A GPU can improve performance, but many small models can run on a CPU. Speed depends on your hardware and model settings.

Model download size is not the same as runtime memory use. The model, context window, operating system, and other applications all affect RAM requirements.

## 3. Install Ollama

Download Ollama from the official page:

**https://ollama.com/download**

### Windows

1. Download the Windows installer.
2. Run the installer and complete setup.
3. Open PowerShell or Command Prompt.
4. Verify the installation:

   ```powershell
   ollama --version
   ```

If the command is not found, reopen the terminal. If it still fails, check that installation completed successfully.

### macOS

1. Download the macOS version from the official download page.
2. Install and open Ollama.
3. Open Terminal and run:

   ```bash
   ollama --version
   ```

### Linux

The official installation command is:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verify the installation:

```bash
ollama --version
```

On a system using systemd, check the service:

```bash
systemctl status ollama
```

If needed, consult the official Linux documentation for service setup and startup instructions.

Official documentation: **https://docs.ollama.com/**

## 4. Download a model

For this guide, use a compact model to keep the first exercise manageable. For example, `qwen3:1.7b`:

```bash
ollama pull qwen3:1.7b
```

This downloads the model. It does not start a chat session.

List the models installed locally:

```bash
ollama list
```

You can explore other available models at **https://ollama.com/library**. Model tags, sizes, and requirements may change, so check the model page before downloading.

## 5. Run the model interactively

Start a chat session:

```bash
ollama run qwen3:1.7b
```

Enter a prompt, such as:

```text
Explain the difference between data engineering and data science in three bullet points.
```

Ollama will generate a response. Try another prompt to continue the conversation.

Exit the interactive session with:

```text
/bye
```

Useful commands:

| Command | Purpose |
|---|---|
| `ollama --version` | Show the installed version |
| `ollama pull qwen3:1.7b` | Download a model |
| `ollama run qwen3:1.7b` | Start interactive inference |
| `ollama list` | List downloaded models |
| `ollama show qwen3:1.7b` | Show model details |
| `ollama ps` | Show models currently loaded in memory |
| `ollama stop qwen3:1.7b` | Stop a loaded model |

Replace the model tag in these commands if you choose a different model.

## 6. Understand the local API

Ollama usually serves its local API at:

```text
http://localhost:11434
```

The API allows local programs to send prompts and receive generated text. The Ollama application or server must be running before a Python client can connect.

You can test the API with curl:

```bash
curl http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3:1.7b",
    "messages": [
      {
        "role": "user",
        "content": "What is a large language model?"
      }
    ],
    "stream": false
  }'
```

On Windows PowerShell, the following is an alternative:

```powershell
$body = @{
    model = "qwen3:1.7b"
    messages = @(
        @{
            role = "user"
            content = "What is a large language model?"
        }
    )
    stream = $false
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
    -Uri "http://localhost:11434/api/chat" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

The returned JSON includes a `message.content` field containing the generated answer.

## 7. Create a Python project

Create a project directory and move into it:

```bash
mkdir ollama-python-demo
cd ollama-python-demo
```

### Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, follow your organization's policy or use Command Prompt with:

```bat
.venv\Scripts\activate.bat
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the official Ollama Python client:

```bash
python -m pip install --upgrade pip
python -m pip install ollama
```

The Python package is a client for the Ollama runtime. It does not itself download the model. Download the model with `ollama pull` first.

## 8. Python inference script

Create a file named `inference.py` in the project directory:

```python
import ollama

MODEL_NAME = "qwen3:1.7b"


def run_inference(prompt: str) -> str:
    """Send a prompt to the local Ollama model and return its answer."""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant. "
                    "Answer clearly and concisely."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return response.message.content


if __name__ == "__main__":
    prompt = (
        "Explain how a data pipeline works "
        "using a simple real-world example."
    )

    try:
        answer = run_inference(prompt)
        print("Prompt:", prompt)
        print("\nLLM response:\n")
        print(answer)

    except ollama.ResponseError as exc:
        print(f"Ollama returned an error: {exc}")
    except Exception as exc:
        print(f"Could not connect to Ollama: {exc}")
```

Run the script:

```bash
python inference.py
```

The exact wording of the answer will vary. The script sends a prompt to the local model and prints the generated text.

### How the script works

1. `MODEL_NAME` selects the downloaded model.
2. `ollama.chat()` sends a list of messages to the local runtime.
3. The `system` message describes the assistant's behaviour.
4. The `user` message contains the task.
5. `response.message.content` extracts the generated answer.
6. The exception handlers print basic diagnostics if a request fails.

This is inference, not model training.

## 9. Keep the model loaded for repeated requests

Ollama can keep a model loaded in memory after a request. This can reduce the delay before later requests because the model may not need to be loaded again.

Example:

```python
import ollama

response = ollama.chat(
    model="qwen3:1.7b",
    messages=[
        {
            "role": "user",
            "content": "Explain vector databases in three bullet points.",
        }
    ],
    keep_alive="30m",
)

print(response.message.content)
```

`keep_alive="30m"` requests that the model remain loaded for 30 minutes after the request. Ollama also supports other values, including a request for indefinite retention. Refer to the current FAQ for exact behaviour: **https://docs.ollama.com/faq**

**Important distinction:** keeping a model loaded does not mean it continuously generates text. An idle model occupies memory but generally does not perform continuous inference. Active generation uses CPU/GPU resources and can affect heat and battery life. Runtime conditions or memory pressure may also affect whether a model remains loaded.

## 10. Optional: Create a custom model configuration

A `Modelfile` can define a reusable configuration based on an existing model. It can set a system prompt and parameters; it does not automatically fine-tune the underlying model.

Create a file named `Modelfile`:

```text
FROM qwen3:1.7b

SYSTEM """
You are a data engineering instructor.
Explain concepts with practical examples
and concise, beginner-friendly answers.
"""

PARAMETER temperature 0.3
```

Create a custom model:

```bash
ollama create data-engineering-assistant -f Modelfile
```

Run it:

```bash
ollama run data-engineering-assistant
```

To use it in Python, change the model name:

```python
MODEL_NAME = "data-engineering-assistant"
```

## 11. Troubleshooting

| Problem | Suggested action |
|---|---|
| `ollama` command not found | Reopen the terminal; confirm installation and PATH setup. |
| Connection refused | Start the Ollama application or server and check the local API. |
| Model not found | Run `ollama pull qwen3:1.7b`, then check `ollama list`. |
| Python cannot import `ollama` | Activate the correct virtual environment and install the package there. |
| Inference is slow | Try a smaller model, shorten prompts, and close memory-intensive applications. |
| Out of memory | Use a smaller model or reduce context length and other resource demands. |
| Laptop becomes hot or battery drains quickly | Reduce active requests, avoid unnecessary background work, and use a shorter keep-alive duration. |

Official troubleshooting guide: **https://docs.ollama.com/troubleshooting**

## 12. Student practical checklist

- [ ] Install Ollama.
- [ ] Verify the installation with `ollama --version`.
- [ ] Download a model using `ollama pull`.
- [ ] Verify the model using `ollama list`.
- [ ] Run an interactive prompt with `ollama run`.
- [ ] Create and activate a Python virtual environment.
- [ ] Install the `ollama` Python package.
- [ ] Run `inference.py`.
- [ ] Inspect loaded models with `ollama ps`.
- [ ] Try a different prompt and record the response time.
- [ ] Optionally create and run a custom `Modelfile`.

### Review questions

1. What is Ollama responsible for?
2. What is the difference between a model download and inference?
3. Why can runtime memory use be larger than the model's download size?
4. What is the role of the Python Ollama client?
5. What does `keep_alive="30m"` request?
6. Does a loaded, idle model continuously generate text?
7. What changes when you create a custom model using a `Modelfile`?

## 13. Official references

- Ollama download page: https://ollama.com/download
- Ollama model library: https://ollama.com/library
- Ollama documentation: https://docs.ollama.com/
- Ollama FAQ: https://docs.ollama.com/faq
- Ollama troubleshooting: https://docs.ollama.com/troubleshooting
- Ollama Python library: https://github.com/ollama/ollama-python

---

**Learning outcome:** After completing this guide, you should be able to install Ollama, download and run a local LLM, call it from Python, and configure a model to remain loaded for repeated requests.
