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

def picture_message():
    print(Style.BRIGHT + Back.LIGHTCYAN_EX + Fore.MAGENTA + "Initializing Picture Agent 🚀".center(50) + Style.RESET_ALL + '\n')
    time.sleep(2)
    print(Style.BRIGHT + Back.RED + Fore.GREEN + "Searching for Pictures 📸".center(50) + Style.RESET_ALL + '\n')

def search_message():
    print(Style.BRIGHT + Back.GREEN + Fore.BLACK + "Search Complete. Sending results to Execution Agent".center(50) + Style.RESET_ALL + '\n')
    
def compiler_message(output):
    print(Style.BRIGHT + Fore.YELLOW + "=" * 50)  
    print(Style.BRIGHT + Fore.CYAN + "COMPILER OUTPUT".center(50)) 
    print(Style.BRIGHT + Fore.YELLOW + "=" * 50)  
    print(Style.NORMAL + Fore.WHITE + output['output'] + Style.RESET_ALL) 
    print(Style.BRIGHT + Fore.YELLOW + "=" * 50 + '\n')  

def user_message(msg_to_user):
        print(Style.BRIGHT + Back.BLUE + Fore.YELLOW + msg_to_user.center(50) + Style.RESET_ALL + '\n')

def refresh_message(response):
    print(Style.BRIGHT + Back.MAGENTA + Fore.WHITE + response.center(50) + Style.RESET_ALL + '\n')

def initial_message():
    msg_to_user = "Type 'refresh' to erase agent's memory 🧠"
    print(Style.BRIGHT + Back.YELLOW + Fore.BLUE + msg_to_user.center(50) + Style.RESET_ALL)
    msg_to_user = "Type 'exit' to leave the chat 🚪"
    print(Style.BRIGHT + Back.GREEN + Fore.WHITE + msg_to_user.center(50) + Style.RESET_ALL + '\n')
