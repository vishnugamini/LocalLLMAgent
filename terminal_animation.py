import sys
import time
import threading
from colorama import Fore, Style, Back

def thinking_dots():
    while getattr(threading.current_thread(), "do_run", True):
        for i in range(4):
            sys.stdout.write(f"{Style.BRIGHT + Fore.YELLOW + Back.BLACK}\rThinking{'.' * i}{' ' * (3 - i)}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.5)

def search_dots():
    while getattr(threading.current_thread(), "do_run", True):
        for i in range(4):
            sys.stdout.write(f"{Style.BRIGHT + Fore.CYAN + Back.RED }\rInitiating Search Agent to browse the Internet{'.' * i}{' ' * (3 - i)}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.5)
