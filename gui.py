import tkinter as tk
from pathlib import Path
import importlib
from models.base_classes import ITU

# todo: solve the warning creation made by itu models

# ignore runtime warnings throwns by numpy
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)

# locating the path of the subpackage models
p = Path(__file__).parent.joinpath("models")

# populating the dict of the implemented ITU models
itu_dict = {}
for module in p.iterdir():
    if "itu" in module.stem:
        # getting the itu python definition file
        m = importlib.import_module(p.name + "." + module.stem)

        # calling the class to instantiate an object at the same time
        itu_dict[module.stem] = getattr(m, module.stem.upper())()


# todo: remove CustomWidget and make the other classes inehrit from tkinter widget classes
class CustomWidget:
    def __init__(self, master):
        # master window
        self.master = master

        # frame contening all the widgets of this class
        self.frame = tk.Frame(self.master)

        # keeping a track to the current displayed image or the GC removes it
        # and tkinter makes it appear empty
        self.image = None

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def grid_forget(self):
        self.frame.grid_forget()


class SearchZone(CustomWidget):
    def __init__(self, master, set_itu_command, lb_height=30):
        super().__init__(master)

        # keeping track of the set_itu_command
        self.set_itu_command = set_itu_command

        # definition of the listbox widget listing all the itu
        self.lb_itu = tk.Listbox(self.frame, height=lb_height)
        self.lb_itu.bind("<<ListboxSelect>>", self._on_listbox_select)

        # filters to update the lisbox based on what the search bar has inside it
        # filter by name
        self.f = lambda x: True if self.sv_search.get() in x else False
        # todo: filter by tags
        # filter list
        self.f_list = [self.f]
        # making the global filter out of the filter list
        self.f_global = lambda x: True in [f(x) for f in self.f_list]

        # itu collections to populate the listbox
        self.itu_list = set(itu_dict.keys())  # using set to get an immutable object
        self.itu_list_display = list(self.itu_list)

        # string variable for the search bar
        self.sv_search = tk.StringVar(self.frame)
        self.sv_search.trace("w", lambda name, index, mode: self.filter_itu(name, index, mode))

        # search bar
        self.entry_search = tk.Entry(self.frame, textvariable=self.sv_search, width=20)

        # init of the listbox
        self.populate_lb_itu()

        # display the widgets inside the frame
        self.entry_search.grid(row=0, column=0)
        self.lb_itu.grid(row=1, column=0)

    def filter_itu(self, *args):

        self.itu_list_display = list(filter(self.f, self.itu_list))
        self.populate_lb_itu()

    def populate_lb_itu(self):

        self.lb_itu.delete(0, tk.END)
        for x in self.itu_list_display:
            self.lb_itu.insert(tk.END, x)

    def _on_listbox_select(self, event: tk.Event):
        print(type(event))
        widget = event.widget  # current listbox
        selection = widget.curselection()

        # do stuff only if the event is fired by the listbox of this widget
        if widget is self.lb_itu:
            index_selection = selection[0]  # mode BROWSE by default so only one element
            itu = itu_dict[self.lb_itu.get(index_selection)]
            self.set_itu_command(itu)


class DisplayZone(CustomWidget):
    def __init__(self, master, get_itu_command):
        super().__init__(master)

        # keeping track of the get_itu_command
        self.get_itu_command = get_itu_command

        # definiton of the widgets
        self.canvas = tk.Canvas(self.frame, width=640, height=480)
        self.btn_draw = tk.Button(self.frame, text="Draw", command=self.draw)

        # display of the widgets
        self.canvas.grid()
        self.btn_draw.grid()

    def draw(self):
        pass


class Gui:
    def __init__(self, name: str, maximised=False):
        # init of the main window
        self.main_window = tk.Tk()
        self.main_window.title(name)

        # open the GUI in maximized mode
        if maximised:
            w, h = self.main_window.winfo_screenwidth(), self.main_window.winfo_screenheight()
            self.main_window.geometry("%dx%d+0+0" % (w, h))

        # current selected itu
        self.current_itu = None

        # declaration of the multiple widgets of the GUI
        self.search_zone = SearchZone(self.main_window, self.set_current_itu)
        self.display_zone = DisplayZone(self.main_window, self.get_current_itu)

        # display of the widgets
        self.search_zone.grid(row=0, column=0)
        self.display_zone.grid(row=0, column=1)

        self.main_window.mainloop()

    def set_current_itu(self, itu: ITU):
        print("got called")
        self.current_itu = itu
        print(self.current_itu)

    def get_current_itu(self):
        return self.current_itu


if __name__ == "__main__":
    a = Gui("gui")
