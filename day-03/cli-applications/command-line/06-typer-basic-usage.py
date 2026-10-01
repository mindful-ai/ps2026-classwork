'''

typer is created by the same author as FastAPI (Sebastián Ramírez).
It’s designed to:
    Make CLIs intuitive and easy to write.
    Automatically handle type conversion, help messages, and completion scripts.
    Feel like writing normal Python functions.

pip install typer

'''

import typer

def greet(name: str, age: int = 18):
    typer.echo(f"Hello {name}, you are {age} years old!")

if __name__ == "__main__":
    typer.run(greet)


'''
C:\mindful-ai\ust-global-python-fs\day-12\command-line>python 06-using-typer.py Sunil --age 35
Hello Sunil, you are 35 years old!

C:\mindful-ai\ust-global-python-fs\day-12\command-line>python 06-using-typer.py --help
Usage: 06-using-typer.py [OPTIONS] NAME

Arguments:
  NAME  [required]

Options:
  --age INTEGER         [default: 18]
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.

  --help                Show this message and exit.

C:\mindful-ai\ust-global-python-fs\day-12\command-line>python 06-using-typer.py Suni --age twenty
Usage: 06-using-typer.py [OPTIONS] NAME
Try '06-using-typer.py --help' for help.

Error: Invalid value for '--age': twenty is not a valid integer


'''