import tkinter as tk
from tkinter.messagebox import showerror, showwarning
from pathlib import Path
import importlib

from PIL import Image, ImageTk

from models.base_classes import ITU, Model

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
        self.lb_itu.bind_all("<<ListboxSelect>>", self._on_listbox_select, "+")

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

        #
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
        widget = event.widget  # current listbox

        print(widget, self.lb_itu)
        selection = widget.curselection()

        # do stuff only if the event is fired by the listbox of this widget
        if widget is self.lb_itu:
            index_selection = selection[0]  # mode BROWSE by default so only one element
            itu = itu_dict[self.lb_itu.get(index_selection)]
            self.set_itu_command(itu)


class DisplayZone(CustomWidget):
    def __init__(self, master, get_itu_command):
        super().__init__(master)
        # how many parameters are displayed on the same line before going to the next line
        self.MAX_PARAM_COLUMNS = 3

        # lists to hold widgets and variables for model parameters
        self.current_param_widgets = []
        self.current_param_variables = []
        self.current_param_labels = []

        # values for dynamic display of the parameters
        self.row_index_init = 1
        self.column_index_init = 1
        self.row_index = self.row_index_init
        self.column_index = self.column_index_init

        # definition of the widgets to pick the correct model of the itu
        self.lb_model = tk.Listbox(self.frame, height=7)
        self.lb_model.bind_all("<<ListboxSelect>>", self._on_listbox_select, "+")
        self.label_model = tk.Label(self.frame, text="pick a model")

        # definition of the label for the parameter zone
        self.label_parameters = tk.Label(self.frame, text="parameters")

        # keeping track of the get_itu_command
        self.get_itu_command = get_itu_command

        # keeping track of the current itu model
        self.current_itu_model: Model = None

        self.current_image: ImageTk.PhotoImage = None
        self.im: Image = None

        # definiton of the widgets
        self.canvas = tk.Canvas(self.frame, width=640, height=480)
        self.btn_draw = tk.Button(self.frame, text="Draw", command=self.draw)
        self.btn_clear = tk.Button(self.frame, text="Clear", command=self.clear)

        # display of the widgets
        self.canvas.grid(row=20, column=1, columnspan=self.MAX_PARAM_COLUMNS)
        self.btn_draw.grid(row=1, column=self.MAX_PARAM_COLUMNS + 1)
        self.btn_clear.grid(row=2, column=self.MAX_PARAM_COLUMNS + 1)
        self.label_model.grid(row=0, column=0)
        self.lb_model.grid(row=1, column=0, rowspan=20, sticky="ns")
        self.label_parameters.grid(row=0, column=1)

    def _on_listbox_select(self, event: tk.Event):
        print("event fired _display")
        print(event.widget, self.lb_model)
        if not event.widget is self.lb_model:
            self.lb_model.delete(0, tk.END)
            for x in range(self.get_itu_command().model_amount):
                self.lb_model.insert(tk.END, str(x + 1))
        else:
            sel = self.lb_model.curselection()[0]  # only one value in browse mode
            # itu model index starts at 1
            self.current_itu_model = self.get_itu_command().models[sel + 1]
            self.update(self.current_itu_model.parameters_desc)

    def update(self, parameters_desc):
        # removing any previous params from another model
        if len(self.current_param_labels) != 0:
            [x.grid_forget() for x in self.current_param_labels + self.current_param_widgets]
            self.current_param_widgets = []
            self.current_param_labels = []
            self.current_param_variables = []
            self.row_index = self.row_index_init
            self.column_index = self.column_index_init

        # constructing all the widgets for the model
        for k, v in parameters_desc.items():
            curr_widget = None
            curr_variable = None
            curr_label = tk.Label(self.frame, text=k)

            if v[1] is int or v[1] is float or v[1] is str:
                curr_variable = tk.StringVar(self.frame)
                if v[2] == "optional":
                    curr_variable.set(str(v[0]))
                curr_widget = tk.Entry(self.frame, textvariable=curr_variable)

            else:  # boolean
                curr_variable = tk.IntVar(self.frame)
                if v[2] == "optional":
                    curr_variable.set(int(v[0]))
                curr_widget = tk.Checkbutton(self.frame, variable=curr_variable)

            # displaying the current widget and its label
            curr_label.grid(row=self.row_index, column=self.column_index, sticky="wens")
            curr_widget.grid(row=self.row_index + 1, column=self.column_index, sticky="wens")
            if k == "h_size":
                print(self.row_index)

            if self.column_index == self.MAX_PARAM_COLUMNS + 1 - 1:
                self.column_index = self.column_index_init
                self.row_index += 2
            else:
                self.column_index += 1
            self.current_param_widgets.append(curr_widget)
            self.current_param_labels.append(curr_label)
            self.current_param_variables.append(curr_variable)

    def check_param(self, parameters_desc):  # modified version of base_classes.Model.check_param
        def add_errored(errored_params, warning_params, param_name, param):
            if param[3] == "optional":
                warning_params.append((param_name, param[0]))
            else:
                errored_params.append((param_name, param[0]))

        errored_params = []
        warning_params = []
        for k, v in parameters_desc.items():

            if isinstance(v[0], str):  # if the value comes from an entry widget
                if len(v[0]) == 0:
                    add_errored(errored_params, warning_params, k, v)
                    continue

                if not v[2] is str:
                    try:
                        v[0] = v[2](v[0])
                    except TypeError:
                        add_errored(errored_params, warning_params, k, v)
            else:  # it's a boolean
                v[0] = bool(v[0])

        if len(errored_params) != 0:
            error_msg = f"les paramètres suivants sont erronés: {', '.join([k for k, v in errored_params])}"
            showerror(title="parameter error(s)", message=error_msg)
            raise TypeError(error_msg)
        return parameters_desc

    def draw(self):
        if self.current_itu_model is not None:
            default_parameters_desc = self.current_itu_model.parameters_desc
            parameters_desc = {}
            for i, k in enumerate(default_parameters_desc):
                var = self.current_param_variables[i].get()
                parameters_desc[k] = [var] + list(default_parameters_desc[k])

            try:
                self.check_param(parameters_desc)
            except TypeError as e:
                return

            self.current_itu_model.evaluate(plot=True, **{k: v[0] for k, v in parameters_desc.items()})
            im = self.current_itu_model.get_image()
            size = im.size
            self.current_image = ImageTk.PhotoImage(image=im)
            print(type(self.current_image))
            self.canvas.im_id = self.canvas.create_image(size, image=self.current_image, anchor="se")
        else:
            return

    def clear(self):
        if not self.current_itu_model is None:
            self.current_itu_model.clear()
            im = self.current_itu_model.get_image()
            self.current_image = ImageTk.PhotoImage(image=im)
            self.canvas.im_id = self.canvas.create_image(im.size, image=self.current_image, anchor="se")




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
        self.search_zone.grid(row=0, column=0, sticky="wens")
        self.display_zone.grid(row=0, column=1, sticky="wens")

        self.main_window.mainloop()

    def set_current_itu(self, itu: ITU):
        self.current_itu = itu

    def get_current_itu(self):
        return self.current_itu


if __name__ == "__main__":
    a = Gui("gui", maximised=False)
    # model = itu_dict["itu2108"].models[2]
    # x = model.evaluate(plot=True, f=30)
    # im = model.get_image()
    # # im.show()
    # main = tk.Tk()
    # c = tk.Canvas(master=main)
    # print(im.size)
    # i = ImageTk.PhotoImage(image=im)
    # c.create_image((i.width(), i.height()), image=i)
    # c.grid()
    # main.mainloop()
