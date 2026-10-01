import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from . import db

app = typer.Typer()
console = Console()

@app.command()
def create(name: str):
    pin = Prompt.ask("[bold green]Enter a 4-digit PIN[/bold green]", password=True)
    try:
        acc = db.create_account(name, pin)
        console.print(f"[bold green]✅ Account created[/bold green]")
        console.print(f"[cyan]ID:[/cyan] {acc.account_id} | [cyan]Balance:[/cyan] ₹{acc.balance:.2f}")
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")

@app.command()
def deposit(account_id: str, amount: float):
    pin = Prompt.ask("[bold green]Enter your PIN[/bold green]", password=True)
    try:
        acc = db.deposit(account_id, pin, amount)
        console.print(f"[bold green]💰 Deposit successful![/bold green] New balance: ₹{acc.balance:.2f}")
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")

@app.command()
def withdraw(account_id: str, amount: float):
    pin = Prompt.ask("[bold green]Enter your PIN[/bold green]", password=True)
    try:
        acc = db.withdraw(account_id, pin, amount)
        console.print(f"[bold green]💸 Withdrawal successful![/bold green] New balance: ₹{acc.balance:.2f}")
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")

@app.command()
def update(account_id: str, new_name: str):
    pin = Prompt.ask("[bold green]Enter your PIN[/bold green]", password=True)
    try:
        acc = db.update_name(account_id, pin, new_name)
        console.print(f"[bold green]✅ Account updated![/bold green] New name: {acc.name}")
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")

@app.command(name="list-all")
def list_all():
    accounts = db.list_accounts()
    if not accounts:
        console.print("[bold yellow]📭 No accounts found.[/bold yellow]")
        return

    table = Table(title="Bank Accounts", box=box.SIMPLE_HEAD)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Balance", justify="right", style="green")

    for acc in accounts:
        table.add_row(acc.account_id, acc.name, f"₹{acc.balance:.2f}")

    console.print(table)
