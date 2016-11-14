from tkinter import *
root = Tk()
l = Listbox(root, width = 15)
l.pack()
l.insert(END, "Hello")
l.insert(END, "world")
l.insert(END, "here")
l.insert(END, "is")
l.insert(END, "an")
l.insert(END, "example")

def close():
    global l, root
    items = l.get(0, END)
    print(items)
    root.destroy()

b = Button(root, text = "OK", command = close).pack()
root.mainloop()