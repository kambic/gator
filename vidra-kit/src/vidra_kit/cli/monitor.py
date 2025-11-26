import typer


monitor_cli = typer.Typer(help="[subcommand] Monitor worker")


@monitor_cli.command("workers")
def list_workers():
    """List all connected Celery workers."""
    response = celery_app.control.ping()
    if not response:
        typer.echo("No workers online.")
    else:
        for worker in response:
            for name in worker:
                typer.echo(f"Worker online: {name}")


@monitor_cli.command("registered")
def list_registered():
    """Show tasks registered by workers."""
    output = celery_app.control.inspect().registered()
    if output:
        for worker, tasks in output.items():
            typer.echo(f"\n[Worker: {worker}]\n" + "\n".join(tasks))
    else:
        typer.echo("No data received. Are workers running?")


@monitor_cli.command("active")
def show_active():
    """Show currently executing tasks."""
    output = celery_app.control.inspect().active()
    if output:
        for worker, tasks in output.items():
            typer.echo(f"\n[Worker: {worker}]")
            for task in tasks:
                typer.echo(f"- {task['name']} (ID: {task['id']}) Args: {task['args']}")
    else:
        typer.echo("No active tasks.")


@monitor_cli.command("reserved")
def show_reserved():
    """Show tasks reserved by the workers (waiting to run)."""
    output = celery_app.control.inspect().reserved()
    if output:
        for worker, tasks in output.items():
            typer.echo(f"\n[Worker: {worker}] Reserved tasks: {len(tasks)}")
            for task in tasks:
                typer.echo(f"- {task['name']} (ID: {task['id']}) Args: {task['args']}")
    else:
        typer.echo("No reserved tasks.")


@monitor_cli.command("scheduled")
def show_scheduled():
    """Show scheduled (ETA/countdown) tasks."""
    output = celery_app.control.inspect().scheduled()
    if output:
        for worker, tasks in output.items():
            typer.echo(f"\n[Worker: {worker}] Scheduled tasks: {len(tasks)}")
            for task in tasks:
                typer.echo(f"- {task['name']} (ID: {task['id']}) ETA: {task['eta']}")
    else:
        typer.echo("No scheduled tasks.")


@monitor_cli.command("stats")
def show_stats():
    """Show worker statistics (processed, failed, uptime, etc)."""
    output = celery_app.control.inspect().stats()
    if output:
        for worker, stats in output.items():
            typer.echo(f"\n[Worker: {worker}]")
            for key, value in stats.items():
                typer.echo(f"{key}: {value}")
    else:
        typer.echo("No stats available.")
