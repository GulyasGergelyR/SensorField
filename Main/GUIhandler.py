from tkinter import *
from tkinter import ttk

from Field.FieldHandler import Field


class GUIHandler:

    def __init__(self):
        self._root = Tk()
        self._canvas = None
        self._init_properties()
        self._create_menu()
        self._create_main_frames(self._root)

        self._field = None

    @staticmethod
    def _do_nothing():
        pass
        """
        filewin = Toplevel(self._root)
        button = Button(filewin, text="Do nothing button")
        button.pack()
        """

    def _init_properties(self):
        self._root.wm_title("SensorField v0.1")

    def _create_menu(self):
        menubar = Menu(self._root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self._do_nothing)
        filemenu.add_command(label="Open", command=self._do_nothing)
        filemenu.add_command(label="Save", command=self._do_nothing)
        filemenu.add_command(label="Save as...", command=self._do_nothing)
        filemenu.add_command(label="Close", command=self._do_nothing)

        filemenu.add_separator()

        filemenu.add_command(label="Exit", command=self._root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=self._do_nothing)

        editmenu.add_separator()

        editmenu.add_command(label="Cut", command=self._do_nothing)
        editmenu.add_command(label="Copy", command=self._do_nothing)
        editmenu.add_command(label="Paste", command=self._do_nothing)
        editmenu.add_command(label="Delete", command=self._do_nothing)
        editmenu.add_command(label="Select All", command=self._do_nothing)

        menubar.add_cascade(label="Edit", menu=editmenu)
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Help Index", command=self._do_nothing)
        helpmenu.add_command(label="About...", command=self._do_nothing)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self._root.config(menu=menubar)

    def run(self):
        self.draw()
        self._root.mainloop()

    def _canvas_mouse_callback(self, event):
        print("x:"+str(event.x))
        print("y:"+str(event.y))
        if self._field is not None:
            self._field.notify(event)

    def _create_main_frames(self, parent):
        self._canvas = Canvas(parent, width=500, height=500)
        self._canvas.bind("<Button-1>", self._canvas_mouse_callback)
        tabs = self._create_tabs(parent)

        self._canvas.grid(row=0, column=0, rowspan=1, columnspan=1)
        tabs.grid(row=0, column=1, rowspan=1, columnspan=1, sticky=(N, S, W, E))

        parent.columnconfigure(0, weight=5)
        parent.columnconfigure(1, weight=5)
        parent.rowconfigure(0, weight=1)

    @staticmethod
    def _create_tabs(parent):
        n = ttk.Notebook(parent)
        f1 = ttk.Frame(n)   # first page, which would get widgets gridded into it
        f2 = ttk.Frame(n)   # second page

        n.add(f1, text='One')
        n.add(f2, text='Two')
        return n

    def add_field(self, field):
        self._field = field

    def draw(self):
        # Draw cells
        self._field.draw(self._canvas)

if __name__ == "__main__":
    guihandler = GUIHandler()
    field = Field()
    field.create_new_room([[2, 2], [2, 3], [3, 3]])
    field.create_new_room([[1, 1], [1, 2], [1, 3]])
    guihandler.add_field(field)
    guihandler.run()

