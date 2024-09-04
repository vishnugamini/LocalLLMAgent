import sys
import time
import threading
from colorama import Fore
def thinking_dots():
    while getattr(threading.current_thread(), "do_run", True):
        for i in range(4):
            sys.stdout.write(f"{Fore.RED}\rThinking{'.' * i}   ")
            sys.stdout.flush()
            time.sleep(0.5)

def search_dots():
    while getattr(threading.current_thread(), "do_run", True):
        for i in range(4):
            sys.stdout.write(f"{Fore.RED}\rInitiating Internet Search{'.' * i}   ")
            sys.stdout.flush()
            time.sleep(0.5)