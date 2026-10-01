import typer

app = typer.Typer()

@app.command()
def greet(name: str, age: int = 18):
    """Greet the user"""
    typer.echo(f"Hello {name}, {age} years old!")

@app.command()
def add(a: int, b: int):
    """Add two numbers"""
    typer.echo(f"The sum is: {a + b}")

if __name__ == "__main__":
    app()


'''

C:\mindful-ai\ust-global-python-fs\day-12\command-line>python 06-typer-with-multiple-functions.py --help
Usage: 06-typer-with-multiple-functions.py [OPTIONS] COMMAND [ARGS]...

Options:
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.

  --help                Show this message and exit.

Commands:
  add    Add two numbers
  greet  Greet the user

C:\mindful-ai\ust-global-python-fs\day-12\command-line>python 06-typer-with-multiple-functions.py greet Vinil --age 20
Hello Vinil, 20 years old!

C:\mindful-ai\ust-global-python-fs\day-12\command-line>python 06-typer-with-multiple-functions.py add 10 20
The sum is: 30


'''