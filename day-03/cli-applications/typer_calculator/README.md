pip install build

Navigate to the folder that has pyproject.toml
C:\mindful-ai\ust-global-python-fs\day-12\typer_calculator>python -m build

Activate the virtual environment
Then, install the built package using the wheel file
(ust-python-env) C:\mindful-ai\ust-global-python-fs\day-12\typer_calculator\dist>pip install typer_calculator-0.1.0-py3-none-any.whl


(ust-python-env) C:\mindful-ai\ust-global-python-fs\day-12\typer_calculator\dist>calc --help
                                                                                                                                  
 Usage: calc [OPTIONS] COMMAND [ARGS]...                                                                                          

 🧮 A simple command-line calculator built with Typer

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                                        │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.                 │
│ --help                        Show this message and exit.                                                                      │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ add        Add two numbers                                                                                                     │
│ subtract   Subtract two numbers                                                                                                │
│ multiply   Multiply two numbers                                                                                                │
│ divide     Divide two numbers                                                                                                  │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯


(ust-python-env) C:\mindful-ai\ust-global-python-fs\day-12\typer_calculator\dist>calc add 10 5
Result: 15.0

(ust-python-env) C:\mindful-ai\ust-global-python-fs\day-12\typer_calculator\dist>calc subtract 10 5
Result: 5.0

(ust-python-env) C:\mindful-ai\ust-global-python-fs\day-12\typer_calculator\dist>calc multiply 10 5
Result: 50.0

(ust-python-env) C:\mindful-ai\ust-global-python-fs\day-12\typer_calculator\dist>calc divide 10 5  
Result: 2.0