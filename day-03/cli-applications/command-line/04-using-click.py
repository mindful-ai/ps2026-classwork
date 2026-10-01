# pip install click

import click

@click.command()
@click.option("--name", prompt="Your name")
@click.option("--age", type=int, prompt="Your age")
@click.option("--city", default="Unknown")
def greet(name, age, city):
    click.echo(f"Hello {name}, {age} years old, from {city}")

if __name__ == "__main__":
    greet()
