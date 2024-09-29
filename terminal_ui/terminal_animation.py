import sys
import time
import threading
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from rich.panel import Panel
from rich.spinner import Spinner
from rich.align import Align

console = Console()

def initializer():
    spinner = Spinner("dots", text="Initializing Systems ⚙️")
    with console.status(spinner, spinner_style="yellow"):
        while getattr(threading.current_thread(), "do_run", True):
            time.sleep(5)



def thinking_dots():
    spinner = Spinner("dots", text="Thinking 🤔")
    with console.status(spinner, spinner_style="yellow"):
        while getattr(threading.current_thread(), "do_run", True):
            time.sleep(0.5)


def search_dots():
    panel = Panel(
        Text("Initializing Search Agent to Browse the Internet 🔍 ", style="bold red"),
        style="bold bright_cyan",
        title="Search Agent",
        subtitle_align="center",
    )
    console.print(panel, justify= "center")
    spinner = Spinner("dots", text="Searching the web for relavant results")
    with console.status(spinner, spinner_style="red"):
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
        Text("Search Complete. Sending results to Execution Agent", style="bold green"),
        style="bold green",
        title="Search Status",
        subtitle_align="center",
    )
    console.print(panel, justify="center")
    time.sleep(1)


def compiler_message(output):
    title_panel = Panel(
        Align.center("COMPILER OUTPUT", style="bold cyan"),
        border_style="bold yellow",
        padding=(1, 2),
    )

    output_panel = Panel(
        Text(output["output"], style="white"),
        title="Output",
        border_style="green",
        padding=(1, 2),
        expand=False,
    )

    console.print(title_panel, justify="center")

    console.print(output_panel, justify="center")

    console.print("\n")


def user_message(msg_to_user):
    markdown_content = Markdown(msg_to_user)
    panel = Panel(
        markdown_content,
        border_style="cyan bold",  # 
        title="User Message",  
        title_align="left",       
        subtitle="Notification",  
        subtitle_align="right",   
        padding=(1, 2),           
        width=120,                 
    )
    console.print(panel, justify="center")
    time.sleep(2)


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
    time.sleep(1)

def uninstall_module(module_name):
    panel = Panel(
        Text(
            f"Initializing Install Agent to uninstall module: {module_name}",
            style="bold magenta",
        ),
        style="bold cyan",
        title="Install Agent",
        subtitle_align="center",
    )
    console.print(panel, justify="center")
    time.sleep(1)

def child_agent_message():
    panel = Panel(
        Text(
            "Creating a child agent to assign task 🧑‍💻", 
            style="bold cyan"
        ),
        style="bold purple",
        title="Creating Child Agent",
        subtitle_align="left",
    )
    console.print(panel, justify="left")
    time.sleep(2)

def kill_child_agent():
    panel = Panel(
        Text(
            "Child Agent Terminated ⚰️. Passing control back to Superior Agent 🔄", 
            style="bold red"
        ),
        style="bold purple",
        title="Child Agent",
        subtitle_align="left",
    )
    console.print(panel, justify="left")
    time.sleep(2)
