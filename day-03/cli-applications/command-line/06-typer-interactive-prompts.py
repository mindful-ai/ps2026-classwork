import typer

def secure_login(username: str = typer.Option(..., prompt=True), password: str = typer.Option(..., prompt=True, hide_input=True)):
    typer.echo(f"Welcome, {username}!")

if __name__ == "__main__":
    typer.run(secure_login)
