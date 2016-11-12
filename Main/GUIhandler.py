from tkinter import *
from tkinter import ttk

from Field.FieldHandler import Field, Selectable, Cell, Room


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
        self._draw()
        self._root.mainloop()

    def _canvas_mouse_callback(self, event):
        if self._field is not None:
            self._field.notify(event)
        self._update()

    def _create_main_frames(self, parent):
        self._canvas = Canvas(parent, width=500, height=500)
        self._canvas.bind("<Button-1>", self._canvas_mouse_callback)
        tabs = self._create_tabs(parent)

        self._canvas.grid(row=0, column=0, rowspan=1, columnspan=1)
        tabs.grid(row=0, column=1, rowspan=1, columnspan=1, sticky=(N, S, W, E))

        parent.columnconfigure(0, weight=5)
        parent.columnconfigure(1, weight=5)
        parent.rowconfigure(0, weight=1)

    def _update(self):
        if self._selector_var.get() != 'Cell':
            self._btn_create_room.config(state=DISABLED)
        else:
            self._btn_create_room.config(state=NORMAL)
        if self._selector_var.get() != 'Room':
            self._btn_delete_room.config(state=DISABLED)
            self._btn_merge_rooms.config(state=DISABLED)
        else:
            self._btn_delete_room.config(state=NORMAL)
            if len(Selectable.selected_elements) > 1:
                self._btn_merge_rooms.config(state=NORMAL)
            else:
                self._btn_merge_rooms.config(state=DISABLED)

        self._draw()

    def _create_tabs(self, parent):
        n = ttk.Notebook(parent)
        f1 = ttk.Frame(n, width=100)   # first page, which would get widgets gridded into it
        f2 = ttk.Frame(n)   # second page

        # f1
        self._selector_var = StringVar()
        self._selector_var.set("Cell")
        Label(f1, text="Select:").grid(row=0, column=0, sticky="nw")
        modes = [("Cells", "Cell", 0), ("Rooms", "Room", 1), ("Sensors", "Sensor", 2)]

        def sel():
            Selectable.remove_elements()
            Selectable.selector_target = self._selector_var.get()
            self._update()
        for t, v, i in modes:
            Radiobutton(f1, text=t, variable=self._selector_var, value=v, command=sel).grid(row=i, column=0, sticky="nw")

        def create_room():
            selected_elements = Selectable.selected_elements
            temp = []
            for se in selected_elements:
                if isinstance(se, Cell):
                    if se.room_id == -1:
                        temp += [se.pos]
            if len(temp):
                self._field.create_new_room(temp)
                Selectable.remove_elements()
            self._update()
        self._btn_create_room = Button(f1, text='Create Room', width=30, command=create_room)
        self._btn_create_room.grid(row=4, column=0, sticky="nw")

        def delete_room():
            selected_elements = Selectable.selected_elements
            temp = []
            for se in selected_elements:
                if isinstance(se, Room):
                    temp += [se]
            if len(temp):
                self._field.delete_room(temp)
                Selectable.remove_elements()
            self._update()
        self._btn_delete_room = Button(f1, text='Delete Room', width=30, command=delete_room, state=DISABLED)
        self._btn_delete_room.grid(row=5, column=0, sticky="nw")

        def merge_rooms():
            selected_elements = Selectable.selected_elements
            temp = []
            for se in selected_elements:
                if isinstance(se, Room):
                    temp += [se]
            if len(temp) > 1:
                cells = []
                # Create copy of cells
                for room in temp:
                    cells.extend(room.cells)
                # Delete rooms
                self._field.delete_room(temp)
                # Create one room to rule them all
                self._field.create_new_room(cells)
                Selectable.remove_elements()
            self._update()
        self._btn_merge_rooms = Button(f1, text='Merge Rooms', width=30, command=merge_rooms, state=DISABLED)
        self._btn_merge_rooms.grid(row=6, column=0, sticky="nw")

        n.add(f1, text='Create Field')
        n.add(f2, text='Analyze Field')
        return n

    def add_field(self, field):
        self._field = field

    def _draw(self):
        # Draw cells
        self._field.draw(self._canvas)

if __name__ == "__main__":
    guihandler = GUIHandler()
    field = Field()
    field.create_new_room([[2, 2], [2, 3], [3, 3]])
    field.create_new_room([[1, 1], [1, 2], [1, 3]])
    guihandler.add_field(field)
    guihandler.run()

