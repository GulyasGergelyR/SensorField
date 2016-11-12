from tkinter import *
from tkinter import ttk


root = Tk()

def donothing():
    filewin = Toplevel(root)
    button = Button(filewin, text="Do nothing button")
    button.pack()


def init_properties():
    root.wm_title("SensorField v0.1")
    #root.resizable(width=False, height=False)


def create_menu():
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="New", command=donothing)
    filemenu.add_command(label="Open", command=donothing)
    filemenu.add_command(label="Save", command=donothing)
    filemenu.add_command(label="Save as...", command=donothing)
    filemenu.add_command(label="Close", command=donothing)

    filemenu.add_separator()

    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    editmenu = Menu(menubar, tearoff=0)
    editmenu.add_command(label="Undo", command=donothing)

    editmenu.add_separator()

    editmenu.add_command(label="Cut", command=donothing)
    editmenu.add_command(label="Copy", command=donothing)
    editmenu.add_command(label="Paste", command=donothing)
    editmenu.add_command(label="Delete", command=donothing)
    editmenu.add_command(label="Select All", command=donothing)

    menubar.add_cascade(label="Edit", menu=editmenu)
    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Help Index", command=donothing)
    helpmenu.add_command(label="About...", command=donothing)
    menubar.add_cascade(label="Help", menu=helpmenu)

    root.config(menu=menubar)


def run():
    root.mainloop()


def create_main_frames(parent):
    canvas = Canvas(parent, width=500, height=500)
    tabs = create_tabs(parent)

    canvas.grid(row=0, column=0, rowspan=1, columnspan=1)
    tabs.grid(row=0, column=1, rowspan=1, columnspan=1, sticky=(N, S, W, E))

    parent.columnconfigure(0, weight=5)
    parent.columnconfigure(1, weight=5)
    parent.rowconfigure(0, weight=1)


def create_tabs(parent):
    n = ttk.Notebook(parent)
    f1 = ttk.Frame(n)   # first page, which would get widgets gridded into it
    f2 = ttk.Frame(n)   # second page

    n.add(f1, text='One')
    n.add(f2, text='Two')
    return n

if __name__ == "__main__":
    init_properties()
    create_menu()
    create_main_frames(root)
    run()
