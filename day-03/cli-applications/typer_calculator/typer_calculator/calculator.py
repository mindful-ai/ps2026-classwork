import typer

app = typer.Typer(help="🧮 A simple command-line calculator built with Typer")

@app.command()
def add(a: float, b: float):
    """Add two numbers"""
    typer.echo(f"Result: {a + b}")

@app.command()
def subtract(a: float, b: float):
    """Subtract two numbers"""
    typer.echo(f"Result: {a - b}")

@app.command()
def multiply(a: float, b: float):
    """Multiply two numbers"""
    typer.echo(f"Result: {a * b}")

@app.command()
def divide(a: float, b: float):
    """Divide two numbers"""
    if b == 0:
        typer.echo("❌ Error: Division by zero")
        raise typer.Exit(code=1)
    typer.echo(f"Result: {a / b}")

if __name__ == "__main__":
    app()
