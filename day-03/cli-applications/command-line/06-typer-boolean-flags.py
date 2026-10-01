import typer

def create_user(name: str, admin: bool = typer.Option(False, help="Create as admin")):
    typer.echo(f"Creating user: {name}")
    if admin:
        typer.echo("User will have admin privileges.")

if __name__ == "__main__":
    typer.run(create_user)
