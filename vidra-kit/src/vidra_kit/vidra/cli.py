# Subcommand group for project operations (e.g., for a complex project like a data pipeline)
from typer import Typer


from typer import Typer, Option, Argument, Context
from typing import Optional, List
from pathlib import Path
import json  # Switched to JSON for config loading
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
import time  # For sleep in progress simulation

# Initialize Rich console for fancy output
console = Console()


# Create the main Typer app with rich markup support for fancy CLI
# Subcommand group for project operations (e.g., for a complex project like a data pipeline)
app = Typer(
    name="vidra-kit",
    help="Vidra Kit CLI for complex projects with config loading.",
    rich_markup_mode="rich",
)


# Example project command: Run with options
@app.command(name="run")
def project_run(
    ctx: Context,
    tasks: List[str] = Argument(None, help="List of tasks to run."),
    verbose: bool = Option(False, "--verbose", "-v", help="Enable verbose output."),
):
    """
    Run project tasks with config integration.
    """
    config = ctx.meta["config"]
    tasks = tasks or config.get("default_tasks", ["task1", "task2"])

    console.print(
        Panel(f"[bold]Running tasks: {', '.join(tasks)}[/bold]", title="Project Run")
    )

    for task in tasks:
        if verbose:
            console.print(f"[magenta]Executing {task} with verbose logs...[/magenta]")
        else:
            console.print(f"[blue]Executing {task}...[/blue]")
        # Simulate execution
        console.print(f"[green]{task} completed.[/green]")


from .vydra_ping import VydraPing
from pathlib import Path


@app.command()
def ping(provider: str, folder: str, formal: bool = False):
    base = Path(folder)  # / provider

    console.print(Panel(f"[bold]Running tasks: {provider}[/bold]", title="Project Run"))

    verbose = False
    file = Path(
        "/export/isilj/test-staging/orginal_provider_packets/Alteka/ALTK0000000000000001.tar"
    )
    # p = VydraPing(username=provider, filepath=file, keep=True, env="stag")
    # p.enqueue()


@app.command()
def ping_folder(provider: str, folder: str, formal: bool = False):
    base = Path(folder)  # / provider

    console.print(Panel(f"[bold]Running tasks: {provider}[/bold]", title="Project Run"))

    verbose = False
    file = Path(
        "/export/isilj/test-staging/orginal_provider_packets/Alteka/ALTK0000000000000001.tar"
    )

    if file.is_dir():

        for file in base.iterdir():

            if not file.suffix in [".tar"]:
                continue

            # if verbose:
            #     console.print(f"[magenta]Executing {file} with verbose logs...[/magenta]")
            # else:
            #     console.print(f"[blue]Executing {file}...[/blue]")
            # Simulate execution
            console.print(f"[green]{file} pinging.[/green]")

            # print(file)

            p = VydraPing(username=provider, filepath=file, keep=True, env="stag")
            p.enqueue()


if __name__ == "__main__":
    app()
