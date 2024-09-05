import sys
import time
import threading
from colorama import Fore, Style

def thinking_dots():
    while getattr(threading.current_thread(), "do_run", True):
        for i in range(4):
            sys.stdout.write(f"{Style.BRIGHT + Fore.YELLOW}\rThinking{'.' * i}{' ' * (3 - i)}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.5)

def search_dots():
    while getattr(threading.current_thread(), "do_run", True):
        for i in range(4):
            sys.stdout.write(f"{Style.BRIGHT + Fore.CYAN}\rInitiating Search Agent to browse the Internet{'.' * i}{' ' * (3 - i)}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.5)
