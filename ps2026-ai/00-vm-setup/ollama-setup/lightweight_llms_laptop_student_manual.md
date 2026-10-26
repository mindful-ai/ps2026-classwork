# Student Manual: Lightweight LLMs for Continuous Laptop Use

## 1. Objective

This manual helps you choose a small language model (LLM) that can run locally on a laptop using [Ollama](https://ollama.com/). Lightweight models are useful for hands-on exercises in Python, local AI assistants, retrieval-augmented generation (RAG), and agentic workflows.

**Important:** Actual performance depends on your laptop's RAM, CPU/GPU, operating system, model quantization, context length, and workload. Model download size is not the same as the total RAM required while running.

## 2. Recommended lightweight models

The following are practical options to investigate. Sizes are approximate and may vary by Ollama model version and quantization.

| Model | Approx. download size | Suggested laptop RAM | Suitable tasks |
|---|---:|---:|---|
| Qwen 3 0.6B | About 0.5 GB | 4–8 GB | Simple text tasks and classification |
| Llama 3.2 1B | About 1.3 GB | 4–8 GB | Short answers and summarization |
| Qwen 3 1.7B | About 1.4 GB | 8 GB or more | General chat and multilingual tasks |
| Gemma 3 1B | About 0.8 GB | 4–8 GB | Short answers and focused tasks |
| Llama 3.2 3B | About 2 GB | 8–16 GB | General-purpose assistant |
| Qwen 3 4B | About 2.5 GB | 8–16 GB | More involved reasoning and coding |
| Phi-4 Mini | About 2.5 GB | 8–16 GB | Maths, reasoning, and coding |
| Gemma 3 4B | About 3.3 GB | 8–16 GB | General tasks; some variants support images |

These RAM figures are **starting estimates, not guarantees**. Leave memory available for the operating system and other applications. Long prompts and large context windows can increase memory use.

Browse current model variants and sizes in the [Ollama Model Library](https://ollama.com/library). Check the model's page before downloading because tags and quantizations can change.

## 3. Which model should I start with?

### Option A: Llama 3.2 1B — for minimum resource use

A compact model for short summaries, simple classification, and lightweight assistant experiments.

```bash
ollama run llama3.2:1b
```

### Option B: Qwen 3 1.7B — a balanced starting point

A useful model to try for local Python applications, simple RAG demonstrations, and general questions.

```bash
ollama run qwen3:1.7b
```

### Option C: Qwen 3 4B — for stronger responses

Try this if your laptop has enough available memory and you want to experiment with more involved prompts, reasoning, or coding.

```bash
ollama run qwen3:4b
```

**Student tip:** Start with a smaller model and confirm that it works before downloading a larger one.

## 4. Install Ollama and download a model

1. Install Ollama from the [official download page](https://ollama.com/download).
2. Open a new terminal.
3. Check that Ollama is installed:

   ```bash
   ollama --version
   ```

4. Download one model. For example:

   ```bash
   ollama pull qwen3:1.7b
   ```

5. Verify that it is available locally:

   ```bash
   ollama list
   ```

6. Start an interactive session:

   ```bash
   ollama run qwen3:1.7b
   ```

7. Enter a prompt, for example:

   ```text
   Explain vector databases in three bullet points.
   ```

8. Exit the interactive session with:

   ```text
   /bye
   ```

Ollama normally provides a local API at `http://localhost:11434`. Its desktop application or server must be running for client applications to connect.

## 5. Keep a model loaded for repeated requests

Ollama can keep a model loaded in memory so that subsequent requests do not need to reload it immediately. This can reduce the delay between requests.

### Python example

Install the Python client in your active environment:

```bash
python -m pip install ollama
```

Create a file named `keep_model_loaded.py`:

```python
import ollama

MODEL = "qwen3:1.7b"

response = ollama.chat(
    model=MODEL,
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

Run it:

```bash
python keep_model_loaded.py
```

The `keep_alive="30m"` setting requests that Ollama keep the model loaded for 30 minutes after the request. Ollama also supports other keep-alive values; consult the current [Ollama FAQ](https://docs.ollama.com/faq) for details.

### Keep-alive is not continuous generation

- **Loaded and idle:** the model remains in memory but is not continuously generating answers.
- **Generating:** the model actively processes a prompt and produces output, using CPU/GPU resources.
- **Indefinite retention:** Ollama supports requesting indefinite retention with `keep_alive=-1`, but memory pressure, system shutdown, or runtime conditions can still affect availability.

Keeping a model loaded occupies RAM or GPU memory and may affect battery life. For a laptop, a timed keep-alive is often a sensible default.

## 6. Check model and runtime status

List models downloaded to the computer:

```bash
ollama list
```

See which models are currently loaded:

```bash
ollama ps
```

Inspect model information:

```bash
ollama show qwen3:1.7b
```

Stop a loaded model when you no longer need it:

```bash
ollama stop qwen3:1.7b
```

If Ollama is not responding, check that its application or server is running before trying the Python script again.

## 7. Troubleshooting

| Problem | Suggested action |
|---|---|
| `ollama` command not found | Install Ollama and reopen the terminal. |
| Connection refused | Start the Ollama application or server. Check that the local API is reachable. |
| Model not found | Run `ollama pull <model-tag>` and verify with `ollama list`. |
| Slow inference | Try a smaller model, shorten the prompt, and close memory-intensive applications. |
| Out of memory | Use a smaller model or reduce the context length and other resource demands. |
| Python cannot import `ollama` | Activate the correct virtual environment and run `python -m pip install ollama`. |
| Laptop becomes hot or battery drains quickly | Reduce active workload, avoid unnecessary background requests, and use a shorter keep-alive period. |

For further help, see the [Ollama documentation](https://docs.ollama.com/) and [troubleshooting guide](https://docs.ollama.com/troubleshooting).

## 8. Practical student exercise

Complete the following steps:

- [ ] Install Ollama.
- [ ] Download `llama3.2:1b` or `qwen3:1.7b`.
- [ ] Run the model interactively and ask it a question.
- [ ] Install the Ollama Python package in a virtual environment.
- [ ] Run the Python inference example.
- [ ] Run `ollama ps` to inspect loaded models.
- [ ] Compare response speed for two models, if your laptop has enough memory.
- [ ] Record the model tag, download size, approximate response time, and any memory or performance issues.

### Questions for discussion

1. What is the difference between downloading a model and running inference?
2. Why can a model's RAM requirement exceed its download size?
3. What is the difference between a loaded, idle model and a model generating a response?
4. How might a smaller model affect the quality of answers in a RAG application?
5. Why might a timed keep-alive setting be preferable on a laptop?

## 9. Workflow recap

1. Install Ollama.
2. Download a compact model.
3. Test it with `ollama run`.
4. Install the Python client.
5. Call the model from Python.
6. Use `keep_alive` when repeated requests benefit from keeping the model loaded.
7. Monitor memory, responsiveness, and battery usage.

**Outcome:** You will have a local LLM runtime, a downloaded model, and a basic Python inference workflow that can be extended for RAG, local assistants, and agentic-workflow exercises.

## Official references

- [Ollama downloads](https://ollama.com/download)
- [Ollama model library](https://ollama.com/library)
- [Ollama documentation](https://docs.ollama.com/)
- [Ollama FAQ](https://docs.ollama.com/faq)
- [Ollama troubleshooting](https://docs.ollama.com/troubleshooting)
