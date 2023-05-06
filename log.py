from termcolor import colored, cprint
from time import sleep
file = open('/home/kamil/log.txt', 'w')


def log(text="default text", color='white'):
    file.write(colored("      ================      ", color) + "\n")
    file.write(colored(text, color) + "\n")
    file.write(colored("      ================      ", color) + "\n")
    file.flush()
