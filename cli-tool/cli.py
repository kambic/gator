import json
import os
from typing import Optional

import requests
import typer
from decouple import config
from rich import print
from rich.console import Console
from rich.table import Table

# Initialize Typer App and Rich Console
app = typer.Typer()
console = Console()

print("Welcome to the CLI Tool of [bold blue]MediaCMS![/bold blue]", ":thumbs_up:")

# Global Configuration
BASE_URL = 'https://demo.mediacms.io/api/v1'
AUTH_KEY: str = ''
USERNAME: str = ''
EMAIL: str = ''


def set_envs():
    """Reads environment variables from .env file and sets global variables."""
    # Check if .env exists and has content to decide on the initial message
    if os.path.exists('.env'):
        with open('.env', 'r') as file:
            if not file.read(1):
                print("Use the 'login' command to set your credential environment variables.")
                return

    global AUTH_KEY, USERNAME, EMAIL
    # config function reads from .env file
    AUTH_KEY = config('AUTH_KEY', default='')
    USERNAME = config('USERNAME', default='')
    EMAIL = config('EMAIL', default='')


# Load environments on script start
set_envs()


@app.callback()
def main_callback():
    """
    A CLI wrapper for the MediaCMS API endpoints.
    """
    # This function is executed before any command.
    pass


@app.command()
def login():
    """🔐 Login to your account and store credentials."""
    email = typer.prompt('Enter your email address')
    password = typer.prompt('Enter your password', hide_input=True)

    data = {
        "email": email,
        "password": password,
    }

    try:
        response = requests.post(url=f'{BASE_URL}/login', data=data)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        response_json = response.json()
        username = response_json.get("username")
        token = response_json.get("token")
        email_resp = response_json.get("email")

        # Write credentials to .env file
        with open(".env", "w") as file:
            file.writelines(f'AUTH_KEY={token}\n')
            file.writelines(f'EMAIL={email_resp}\n')
            file.writelines(f'USERNAME={username}\n')

        # Update globals immediately
        global AUTH_KEY, USERNAME, EMAIL
        AUTH_KEY = token
        USERNAME = username
        EMAIL = email_resp

        print(f"Welcome to MediaCMS [bold blue]{username}[/bold blue]. Your auth creds have been successfully stored in the .env file", ":v:")

    except requests.exceptions.RequestException as e:
        if response.status_code == 400:
            # Handling specific API error structure for login failure
            print(f'Error: {response.text}')
        else:
            print(f"An error occurred during login: {e}")


@app.command()
def upload_media(
    path: str = typer.Argument(..., help="The path to the file or directory containing files to upload.")
):
    """⬆️ Upload media to the server."""
    if not AUTH_KEY:
        print("[bold red]Error:[/bold red] You must be logged in. Run 'login' first.")
        raise typer.Exit(code=1)

    headers = {'authorization': f'Token {AUTH_KEY}'}

    def process_upload(file_path, filename):
        """Helper function to perform the actual file upload."""
        try:
            with open(file_path, 'rb') as f:
                files = {'media_file': f}
                response = requests.post(url=f'{BASE_URL}/media', headers=headers, files=files)
                response.raise_for_status()

            print(f"[bold blue]{filename}[/bold blue] successfully uploaded!")
        except FileNotFoundError:
            print(f"[bold red]Error:[/bold red] File not found at {file_path}")
        except requests.exceptions.RequestException as e:
            print(f'[bold red]Error uploading {filename}:[/bold red] {response.text if "response" in locals() else e}')

    abs_path = os.path.abspath(path)

    if os.path.isdir(abs_path):
        # Handle directory upload
        print(f"Uploading files from directory: [bold yellow]{abs_path}[/bold yellow]")
        for filename in os.listdir(abs_path):
            file_path = os.path.join(abs_path, filename)
            if os.path.isfile(file_path):
                process_upload(file_path, filename)
            else:
                print(f"Skipping directory/non-file: {filename}")
    elif os.path.isfile(abs_path):
        # Handle single file upload
        filename = os.path.basename(abs_path)
        process_upload(abs_path, filename)
    else:
        print(f"[bold red]Error:[/bold red] Path is neither a file nor a directory: {path}")


@app.command()
def my_media():
    """📜 List all media uploaded by the authorized user."""
    if not AUTH_KEY or not USERNAME:
        print("[bold red]Error:[/bold red] You must be logged in. Run 'login' first.")
        raise typer.Exit(code=1)

    headers = {'authorization': f'Token {AUTH_KEY}'}
    try:
        response = requests.get(url=f'{BASE_URL}/media?author={USERNAME}', headers=headers)
        response.raise_for_status()
        data_json = response.json()

        table = Table(title=f"Media by [bold magenta]{USERNAME}[/bold magenta]", show_header=True, header_style="bold magenta")
        table.add_column("Name of the media", style="dim", no_wrap=True)
        table.add_column("Media Type")
        table.add_column("State")

        if data_json.get('results'):
            for data in data_json['results']:
                table.add_row(data['title'], data['media_type'], data['state'])
            console.print(table)
        else:
            print("[bold yellow]Info:[/bold yellow] No media found for this user.")

    except requests.exceptions.RequestException as e:
        print(f'[bold red]Could not get the media:[/bold red] {response.text if "response" in locals() else e}')


@app.command()
def whoami():
    """👤 Shows the details of the authorized user."""
    if not AUTH_KEY:
        print("[bold red]Error:[/bold red] You must be logged in. Run 'login' first.")
        raise typer.Exit(code=1)

    headers = {'authorization': f'Token {AUTH_KEY}'}
    try:
        response = requests.get(url=f'{BASE_URL}/whoami', headers=headers)
        response.raise_for_status()
        user_data = response.json()

        print("[bold cyan]Authorized User Details:[/bold cyan]")
        for key, value in user_data.items():
            print(f"[bold]{key.replace('_', ' ').title()}[/bold] : {value}")

    except requests.exceptions.RequestException as e:
        print(f'[bold red]Could not get user details:[/bold red] {response.text if "response" in locals() else e}')


@app.command()
def categories():
    """🏷️ List all categories."""
    try:
        response = requests.get(url=f'{BASE_URL}/categories')
        response.raise_for_status()
        data_json = response.json()

        table = Table(title="Media Categories", show_header=True, header_style="bold magenta")
        table.add_column("Category")
        table.add_column("Description")

        for data in data_json:
            table.add_row(data['title'], data['description'])

        console.print(table)
    except requests.exceptions.RequestException as e:
        print(f'[bold red]Could not get the categories:[/bold red] {response.text if "response" in locals() else e}')


@app.command()
def encodings():
    """🗜️ List all encoding profiles."""
    try:
        response = requests.get(url=f'{BASE_URL}/encode_profiles/')
        response.raise_for_status()
        data_json = response.json()

        table = Table(title="Encoding Profiles", show_header=True, header_style="bold magenta")
        table.add_column("Name")
        table.add_column("Extension")
        table.add_column("Resolution")
        table.add_column("Codec")
        table.add_column("Description")

        for data in data_json:
            # Ensure data types are strings for printing in the table
            table.add_row(
                str(data['name']),
                str(data['extension']),
                str(data['resolution']),
                str(data['codec']),
                str(data['description'])
            )
        console.print(table)
    except requests.exceptions.RequestException as e:
        print(f'[bold red]Could not get the encodings:[/bold red] {response.text if "response" in locals() else e}')


if __name__ == '__main__':
    app()
