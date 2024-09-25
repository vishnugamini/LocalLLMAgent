import sys
import time
import threading
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.spinner import Spinner
from rich.align import Align

console = Console()


def sub_thinking_dots():
    spinner = Spinner("bouncingBall", text="Child Agent: Processing 🤔")
    with console.status(spinner, spinner_style="green"):
        while getattr(threading.current_thread(), "do_run", True):
            time.sleep(0.5)


def sub_search_dots():
    panel = Panel(
        Text("Child Agent: Engaging Search Protocols 🔍", style="bold cyan"),
        style="bold red",
        title="Child Agent Search",
        subtitle_align="left",
    )
    console.print(panel, justify="left")
    spinner = Spinner("dots", text="Child Agent: Scanning the web for results")
    with console.status(spinner, spinner_style="green"):
        while getattr(threading.current_thread(), "do_run", True):
            time.sleep(0.5)


def sub_picture_message():
    panel1 = Panel(
        Text("Child Agent: Preparing Image Search 🚀", style="bold cyan"),
        style="bold magenta",
        title="Child Agent Image Search",
        subtitle_align="left",
    )
    console.print(panel1, justify="left")
    time.sleep(2)

    panel2 = Panel(
        Text("Child Agent: Searching for Images 📸", style="bold yellow"),
        style="bold blue",
        title="Child Agent Picture Search",
        subtitle_align="left",
    )
    console.print(panel2, justify="left")
    time.sleep(1)


def sub_search_message():
    panel = Panel(
        Text("Child Agent: Search Complete. Sending data to main agent.", style="bold red"),
        style="bold blue",
        title="Child Agent Search Status",
        subtitle_align="left",
    )
    console.print(panel, justify="left")
    time.sleep(1)


def sub_compiler_message(output):
    title_panel = Panel(
        Align.left("CHILD AGENT: COMPILER OUTPUT", style="bold white"),
        border_style="bold green",
        padding=(1, 2),
    )

    output_panel = Panel(
        Text(output["output"], style="yellow"),
        title="Child Agent Output",
        border_style="magenta",
        padding=(1, 2),
        expand=False,
    )

    console.print(title_panel, justify="left")
    console.print(output_panel, justify="left")
    console.print("\n")


def sub_user_message(msg_to_user):
    panel = Panel(
        Text(msg_to_user, style="bold green"),
        style="bold magenta",
        title="Child Agent User Message",
        subtitle_align="left",
    )
    console.print(panel, justify="left")
    time.sleep(1)


def sub_install_module(module_name):
    panel = Panel(
        Text(
            f"Child Agent: Installing module: {module_name}",
            style="bold green",
        ),
        style="bold yellow",
        title="Child Agent Install",
        subtitle_align="left",
    )
    console.print(panel, justify="left")
    time.sleep(2)

