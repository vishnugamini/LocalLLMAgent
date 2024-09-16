import sys
import time
import threading
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.spinner import Spinner
from rich.align import Align

console = Console()


def thinking_dots():
    spinner = Spinner("dots", text="Thinking 🤔")
    with console.status(spinner, spinner_style="yellow"):
        while getattr(threading.current_thread(), "do_run", True):
            time.sleep(0.5)


def search_dots():
    spinner = Spinner("dots", text="Initiating Search Agent to browse the Internet 🔍")
    with console.status(spinner, spinner_style="cyan on red"):
        while getattr(threading.current_thread(), "do_run", True):
            time.sleep(0.5)


def picture_message():
    panel1 = Panel(
        Text("Initializing Agent to search for Pictures 🚀", style="bold magenta"),
        style="bold bright_cyan",
        title="Picture Agent",
        subtitle_align="center",
    )
    console.print(panel1, justify="center")
    time.sleep(2)

    panel2 = Panel(
        Text("Searching for Pictures 📸", style="bold green"),
        style="bold red",
        title="Picture Search",
        subtitle_align="center",
    )
    console.print(panel2, justify="center")
    time.sleep(1)


def search_message():
    panel = Panel(
        Text("Search Complete. Sending results to Execution Agent", style="bold black"),
        style="bold green",
        title="Search Status",
        subtitle_align="center",
    )
    console.print(panel, justify="center")
    time.sleep(1)


def compiler_message(output):
    if output["error"] == True:
        text = "There seems to be an error in the code. Throughly understand why it arised and mitigate it immediately by fixing the code. Do not make the same error again"
    else:
        text = ""
    title_panel = Panel(
        Align.center("COMPILER OUTPUT", style="bold cyan"),
        border_style="bold yellow",
        padding=(1, 2),
    )

    output_panel = Panel(
        Text(output["output"] + text, style="white"),
        title="Output",
        border_style="green",
        padding=(1, 2),
        expand=False,
    )

    console.print(title_panel, justify="center")

    console.print(output_panel, justify="center")

    console.print("\n")


def user_message(msg_to_user):
    panel = Panel(
        Text(msg_to_user, style="bold yellow"),
        style="bold blue",
        title="User Message",
        subtitle_align="center",
    )
    console.print(panel, justify="center")
    time.sleep(1)


def refresh_message(response):
    panel = Panel(
        Text(response, style="bold white"),
        style="bold magenta",
        title="Refresh",
        subtitle_align="center",
    )
    console.print(panel, justify="center")
    time.sleep(1)


def initial_message():
    msg1 = "Type 'refresh' to erase agent's memory 🧠"
    panel1 = Panel(
        Text(msg1, style="bold blue"),
        style="bold yellow",
        title="Instructions",
        subtitle_align="center",
    )
    console.print(panel1, justify="center")

    msg2 = "Type 'exit' to leave the chat 🚪"
    panel2 = Panel(
        Text(msg2, style="bold white"),
        style="bold green",
        title="Instructions",
        subtitle_align="center",
    )
    console.print(panel2, justify="center")
    time.sleep(1)


def install_module(module_name):
    panel = Panel(
        Text(
            f"Initializing Install Agent to install module: {module_name}",
            style="bold magenta",
        ),
        style="bold cyan",
        title="Install Agent",
        subtitle_align="center",
    )
    console.print(panel, justify="center")
    time.sleep(2)
