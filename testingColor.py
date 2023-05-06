from termcolor import colored, cprint
from time import sleep
file = open('/home/kamil/Fudge.txt', 'w')
file2 = open('/home/kamil/Fudge2.txt', 'w')

text = colored('Hello, World!', 'red')
text2 = colored('Hello, World!', 'green')
while (True):
    file.write(text + "\n")
    file2.write(text2 + "\n")
    file.flush()
    file2.flush()
    sleep(1)
