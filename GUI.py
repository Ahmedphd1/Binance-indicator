from tkinter import *
from tkinter.ttk import *
import sys
from indicatorlibrary import *
from files import *
import threading

screen = Tk()
screen.title("Binance tading bot")
canvas = Canvas(screen, width= 300, height = 300)
canvas.pack()

print("creating new files")
newfiles()

exit_event = threading.Event()


def mainfunction():
    while True:

        if exit_event.is_set():
            break

        if buykdj(exit_event) == False:
            print("exiting program")
            exit_event.set()

def startfunc():
    t = threading.Thread(target=mainfunction, daemon=True)
    t.start()

def stopfunc():
    print("exiting program")
    exit_event.set()

start = Button(screen, text="START", command = startfunc)
canvas.create_window(100,280, window=start)

stop = Button(screen, text="STOP", command = stopfunc)
canvas.create_window(190,280, window=stop)


mainloop()