import tkinter as tk
import tkinter.ttk as ttk
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
        """generic method to mimicate the grid method of the child widgets"""
        self.frame.grid(**kwargs)

    def grid_forget(self):
        """generic method to mimicate the grid_forget method of the child widget"""
        self.frame.grid_forget()


class SearchZone(CustomWidget):
    def __init__(self, master, set_itu_command, lb_height=30):
        super().__init__(master)

        # keeping track of the set_itu_command
        self.set_itu_command = set_itu_command

        # ITU label
        self.label_itu = tk.Label(self.frame, text="recommandation ITU")
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
        self.label_itu.grid(row=0, column=0)
        self.entry_search.grid(row=1, column=0)
        self.lb_itu.grid(row=2, column=0, sticky="ns")

    def filter_itu(self, *args):
        """method used when the entry box for the research is updated"""
        self.itu_list_display = list(filter(self.f, self.itu_list))
        self.populate_lb_itu()

    def populate_lb_itu(self):
        """method used to delete and repopulate the list of all the itu models availiable"""
        self.lb_itu.delete(0, tk.END)
        for x in self.itu_list_display:
            self.lb_itu.insert(tk.END, x)

    def _on_listbox_select(self, event: tk.Event):
        """method called when the user click on a listbox"""
        widget = event.widget  # current listbox
        if not type(widget) is tk.Listbox:  # sometimes it's not a listbox for a unknown reason
            return
        selection = widget.curselection()

        # do stuff only if the event is fired by the listbox of this widget
        if widget is self.lb_itu:
            try:
                index_selection = selection[0]  # mode BROWSE by default so only one element
                itu = itu_dict[self.lb_itu.get(index_selection)]
                self.set_itu_command(itu)
            except IndexError:  # todo: proper handling instead of dumb try/except clauses
                pass


class DisplayZone(CustomWidget):
    def __init__(self, master, get_itu_command):
        super().__init__(master)
        self.plot_addition_widget_instance = None

        # how many parameters are displayed on the same line before going to the next line
        self.MAX_PARAM_COLUMNS = 3

        # lists to hold widgets and variables for model parameters
        self.current_param_widgets = []
        self.current_param_variables = []
        self.current_param_labels = []

        # values for dynamic display of the parameters
        self.row_index_init = 2
        self.column_index_init = 1
        self.row_index = self.row_index_init
        self.column_index = self.column_index_init

        # definition of the widgets to pick the correct model of the itu
        self.lb_model = tk.Listbox(self.frame, height=7)
        self.lb_model.bind_all("<<ListboxSelect>>", self._on_listbox_select, "+")
        self.label_model = tk.Label(self.frame, text="modèle de courbe")

        # definition of the label for the parameter zone
        self.label_parameters = tk.Label(self.frame, text="paramètres")

        # definition of the label for the model name
        self.label_model_name = None

        # keeping track of the get_itu_command
        self.get_itu_command = get_itu_command

        # keeping track of the current itu model
        self.current_itu_model: Model = None

        # keeping track of the current displayed image
        self.current_image: ImageTk.PhotoImage = None

        # definiton of the area holding the image
        self.canvas = tk.Canvas(self.frame, width=640, height=480)

        # definition of the buttons
        self.btn_draw = tk.Button(self.frame, text="Draw", command=self.draw)
        self.btn_clear = tk.Button(self.frame, text="Clear", command=self.clear)
        self.btn_delete_last = tk.Button(self.frame, text="Delete last curve", command=self.delete_last)
        self.btn_delete = tk.Button(self.frame, text="Delete selected curve", command=self.delete)
        self.btn_add_plot = tk.Button(self.frame, text="Add plots", command=self.open_plot_widget)

        # definition of the  combo box for the selection of the curve to delete it
        self.combo_box_curve_deletion = tk.ttk.Combobox(self.frame)

        # display of the widgets
        self.canvas.grid(row=20, column=1, columnspan=self.MAX_PARAM_COLUMNS)

        self.label_model.grid(row=0, column=0)
        self.lb_model.grid(row=1, column=0, rowspan=20, sticky="ns")

        # removing this to avoid button being displayed before the selection of a model

        # self.btn_draw.grid(row=self.row_index_init + 1, column=self.MAX_PARAM_COLUMNS + 1)
        # self.btn_clear.grid(row=self.row_index_init + 2, column=self.MAX_PARAM_COLUMNS + 1)
        # self.btn_delete_last.grid(row=self.row_index_init + 3, column=self.MAX_PARAM_COLUMNS + 1)
        # self.combo_box_curve_deletion.grid(row=self.row_index_init + 4, column=self.MAX_PARAM_COLUMNS + 1)
        # self.btn_delete.grid(row=self.row_index_init + 5, column=self.MAX_PARAM_COLUMNS + 1)
        # self.btn_add_plot.grid(row=self.row_index_init + 6, column=self.MAX_PARAM_COLUMNS + 1)
        # self.label_parameters.grid(row=self.row_index_init - 1, column=self.column_index_init,
        #                            columnspan=self.MAX_PARAM_COLUMNS)

    def _on_listbox_select(self, event: tk.Event):
        """method called when the user click on a listbox"""

        # if the listbox is not the one listing the model list (ie. the one to pick the itu models in SearchZone),
        # updating the listbox listing the model list
        if not event.widget is self.lb_model:
            self.lb_model.delete(0, tk.END)
            for x in range(self.get_itu_command().model_amount):
                self.lb_model.insert(tk.END, str(x + 1))
        # if the listbox is the one listing the model list: updating the model
        else:
            try:
                sel = self.lb_model.curselection()[0]  # only one value in browse mode
                # itu model index starts at 1
                self.current_itu_model = self.get_itu_command().models[sel + 1]
                self.update()
                self.clear()
            except IndexError:
                pass  # todo: make a proper handling instead of dumb try/except clauses

    def update(self):
        """method updating the dynamic widgets for the model parameters"""
        # removing any previous params from another model
        if len(self.current_param_labels) != 0:
            [x.grid_forget() for x in self.current_param_labels + self.current_param_widgets]
            self.current_param_widgets = []
            self.current_param_labels = []
            self.current_param_variables = []
            self.row_index = self.row_index_init
            self.column_index = self.column_index_init

        if not self.label_model_name is None:
            self.label_model_name.grid_forget()

        # updating these widgets:
        self.btn_draw.grid_forget()
        self.btn_clear.grid_forget()
        self.btn_delete_last.grid_forget()
        self.combo_box_curve_deletion.grid_forget()
        self.btn_delete.grid_forget()
        self.btn_add_plot.grid_forget()
        self.label_parameters.grid_forget()

        self.btn_draw.grid(row=self.row_index_init + 1, column=self.MAX_PARAM_COLUMNS + 1, sticky="we")
        self.btn_clear.grid(row=self.row_index_init + 2, column=self.MAX_PARAM_COLUMNS + 1, sticky="we")
        self.btn_delete_last.grid(row=self.row_index_init + 3, column=self.MAX_PARAM_COLUMNS + 1, sticky="we")
        self.combo_box_curve_deletion.grid(row=self.row_index_init + 4, column=self.MAX_PARAM_COLUMNS + 1, sticky="we")
        self.btn_delete.grid(row=self.row_index_init + 5, column=self.MAX_PARAM_COLUMNS + 1, sticky="we")
        self.btn_add_plot.grid(row=self.row_index_init + 6, column=self.MAX_PARAM_COLUMNS + 1, sticky="we")
        self.label_parameters.grid(row=self.row_index_init - 1, column=self.column_index_init,
                                   columnspan=self.MAX_PARAM_COLUMNS)

        self.label_model_name = tk.Label(self.frame, text=self.current_itu_model.title.replace("\n", ""))
        self.label_model_name.grid(row=self.row_index_init - 2, column=self.column_index_init,
                                   columnspan=self.MAX_PARAM_COLUMNS)
        # constructing all the widgets for the model
        for k, v in self.current_itu_model.parameters_desc.items():
            curr_widget = None
            curr_variable = None
            curr_label = tk.Label(self.frame, text=self.current_itu_model.get_mapping(k))

            # autodetect the correct widget type
            if v[1] in [int, float, str]:
                curr_variable = tk.StringVar(self.frame)
                if v[2] == "optional":
                    curr_variable.set(str(v[0]))
                curr_widget = tk.Entry(self.frame, textvariable=curr_variable)

            elif v[1] is ttk.Combobox:
                curr_widget = ttk.Combobox(self.frame, values=v[0])
                curr_widget.current(0)
                curr_variable = curr_widget  # gui will call the get method of this object to retrieve its value

            else:  # boolean
                curr_variable = tk.IntVar(self.frame)
                if v[2] == "optional":
                    curr_variable.set(int(v[0]))
                curr_widget = tk.Checkbutton(self.frame, variable=curr_variable)

            # displaying the current widget and its label
            curr_label.grid(row=self.row_index, column=self.column_index, sticky="wens")
            curr_widget.grid(row=self.row_index + 1, column=self.column_index, sticky="wens")

            # make the grid manager return at the next "line" when the column parameter reach a certain value
            if self.column_index == self.MAX_PARAM_COLUMNS + 1 - 1:
                self.column_index = self.column_index_init
                self.row_index += 2
            else:
                self.column_index += 1

            self.current_param_widgets.append(curr_widget)
            self.current_param_labels.append(curr_label)
            self.current_param_variables.append(curr_variable)

    def check_param(self, parameters_desc):  # modified version of base_classes.Model.check_param
        """method checking the parameters. open a windows with an error message if the parameters are wrong"""

        # todo: avoid redefining this method each time the check_param is called
        def add_errored(errored_params, warning_params, param_name, param):
            if param[3] == "optional":
                warning_params.append((param_name, param[0]))
            else:
                errored_params.append((param_name, param[0]))

        # todo: make an actual use of the warning_params
        errored_params = []
        warning_params = []
        for k, v in parameters_desc.items():
            # if the value comes from an entry widget
            if isinstance(v[0], str):
                if len(v[0]) == 0:  # empty entrybox
                    add_errored(errored_params, warning_params, k, v)
                    continue

                if v[2] in [ttk.Combobox]:
                    pass

                else:
                    # if the parameter is supposed to be something else than a string (primitive type casting)
                    if not v[2] is str:
                        try:
                            v[0] = v[2](v[0])
                        except TypeError:
                            add_errored(errored_params, warning_params, k, v)

            # it's a boolean
            else:
                v[0] = bool(v[0])

        # opening the error windows if at least one parameter is errored
        if len(errored_params) != 0:
            error_msg = f"les paramètres suivants sont erronés: {', '.join([k for k, v in errored_params])}"
            showerror(title="parameter error(s)", message=error_msg)
            raise TypeError(error_msg)
        return parameters_desc

    def draw(self):
        """method called to draw the image of the current model"""
        if self.current_itu_model is not None:  # if it is defined

            default_parameters_desc = self.current_itu_model.parameters_desc

            # gathering the parameters from the GUI
            parameters_desc = {}
            for i, k in enumerate(default_parameters_desc):
                var = self.current_param_variables[i].get()
                parameters_desc[k] = [var] + list(default_parameters_desc[k])

            # checks the parameters gathered from the GUI
            try:
                self.check_param(parameters_desc)
            except TypeError as e:
                return

            # evaluating and drawing the image inside the canvas
            self.current_itu_model.evaluate(plot=True, **{k: v[0] for k, v in parameters_desc.items()})
            self.update_image()

    def update_image(self):
        """
        method used to update the figure of the current itu model displayed in the GUI
        """
        if self.current_itu_model.figure is None:
            return

        # refreshing the image
        im = self.current_itu_model.get_image()
        self.current_image = ImageTk.PhotoImage(image=im)
        self.canvas.im_id = self.canvas.create_image(im.size, image=self.current_image, anchor="se")
        self.populate_combobox_removal()

    def populate_combobox_removal(self):
        """
        method called to update the combobox holding all the plot names
        """
        figure = self.current_itu_model.figure
        if figure is None:
            return

        values = [f"{i + 1}) " + line.get_label() for i, line in enumerate(figure.gca().get_lines())]
        if len(values) == 0:
            values = [""]
        self.combo_box_curve_deletion.configure(values=values)
        self.combo_box_curve_deletion.current(0)

    def clear(self):
        """method used to removing the current curves on the current image of the current model"""
        if not self.current_itu_model is None:
            # clearing the internal image of the model
            self.current_itu_model.clear()
            self.update_image()

    def delete_last(self):
        """
        deletes the last plot from the current itu model figure
        """
        try:
            self.current_itu_model.delete_last_curve()
            self.update_image()
        except IndexError:
            pass

    def delete(self):
        """
        deletes the corresponding curve in the combobox from the current itu model figure
        """
        selected_value = self.combo_box_curve_deletion.get()
        if selected_value == "":  # if this is called when the combobox is empty
            return

        selected_index = int(selected_value.split(")")[0])
        self.current_itu_model.delete_curve(selected_index)
        self.update_image()
        self.populate_combobox_removal()
        self.combo_box_curve_deletion.update()

    def open_plot_widget(self):
        """
        open the PlotAdditionWindow widget at most one time.
        """
        if self.plot_addition_widget_instance is None:
            self.plot_addition_widget_instance = PlotAdditionWindow(self.current_itu_model, self)

    def unbind_plot_addition_window(self):
        """
        removes the instance of the PlotAdditionWindow
        """
        self.plot_addition_widget_instance = None


class PlotAdditionWindow:
    """
    Class used to create a widget that will gather user data and plot it on the current itu model figure.
    """
    def __init__(self, current_itu_model, root_widget):
        self.current_itu_model = current_itu_model
        self.root_widget = root_widget
        self.toplevel = tk.Toplevel(self.root_widget.master)

        # catching the windows destruction event and binding a method on this event
        self.toplevel.protocol('WM_DELETE_WINDOW', self.unbind)

        # string variables to get X/Y arrays
        self.sv_x = tk.StringVar(self.toplevel)
        self.sv_y = tk.StringVar(self.toplevel)
        self.sv_label = tk.StringVar(self.toplevel)

        # various internal parameters
        self.entry_width = 50
        self.column_start_index = 0

        # creation of labels
        self.label_x = tk.Label(self.toplevel, text="X array")
        self.label_y = tk.Label(self.toplevel, text="Y array")
        self.label_label = tk.Label(self.toplevel, text="Legend")

        # creation of the entries
        self.entry_x = tk.Entry(self.toplevel, textvariable=self.sv_x, width=self.entry_width)
        self.entry_y = tk.Entry(self.toplevel, textvariable=self.sv_y, width=self.entry_width)
        self.entry_label = tk.Entry(self.toplevel, textvariable=self.sv_label, width=self.entry_width)

        # creation of the buttons
        self.btn_reset = tk.Button(self.toplevel, text="Reset fields", command=self.reset_fields)
        self.btn_add = tk.Button(self.toplevel, text="Add plot", command=self.add_plot)

        # display
        self.label_x.grid(row=self.row_start_index, column=0, columnspan=2)
        self.entry_x.grid(row=self.row_start_index + 1, column=0, columnspan=2)

        self.label_y.grid(row=self.row_start_index + 2, column=0, columnspan=2)
        self.entry_y.grid(row=self.row_start_index + 3, column=0, columnspan=2)

        self.label_label.grid(row=self.row_start_index + 4, column=0, columnspan=2)
        self.entry_label.grid(row=self.row_start_index + 5, column=0, columnspan=2)

        self.btn_reset.grid(row=self.row_start_index + 6, column=0, sticky="we")
        self.btn_add.grid(row=self.row_start_index + 6, column=1, sticky="we")

    def reset_fields(self):
        """function to clear the Entry widgets"""
        self.sv_x.set("")
        self.sv_y.set("")
        self.sv_label.set("")

    def add_plot(self):
        """function to add a curve from the user data"""
        def process_string(string, delimiter=";"):
            """
            function to convert a string into an array of float. Will throw a ValueError if the string can't be processed
            """
            # replacing "," with "." to avoid upsetting the user too much in case he inserted large amount of data with
            # wrong symbol
            elems = [float(elem.strip(" ").replace(",", ".")) for elem in string.split(delimiter)]
            return elems

        error_dict = {}

        def check_array(string, array_name, delimiter=";"):
            """function to check validity of array data strings"""
            if string == "":
                return array_name + " data is empty"
            else:
                try:
                    process_string(string)
                except ValueError:
                    return f"error parsing following {array_name} data: " + string

        error_x_array = check_array(self.sv_x.get(), "x")
        error_y_array = check_array(self.sv_y.get(), "y")

        # x array data checking
        if error_x_array is None:
            x_array = process_string(self.sv_x.get())
        else:
            error_dict["x_array"] = error_x_array

        # y array data checking
        if error_y_array is None:
            y_array = process_string(self.sv_y.get())
        else:
            error_dict["y_array"] = error_y_array

        # label checking
        label = self.sv_label.get()
        if label == "":
            error_dict["label"] = "legend is empty"

        # if at least one error is detected, display them to the user
        if len(error_dict) != 0:
            error_message = "Following errors were caught during the data verification:\n" + \
                            "\n".join([error for error in error_dict.values()])
            showerror("data parsing error", message=error_message)

        # if everything went well, plotting the curve
        else:
            self.current_itu_model.plot(x_array, y_array, label)
            self.root_widget.update_image()

    def unbind(self):
        """# function to unbind this instance, as it's currently destroyed"""
        self.root_widget.unbind_plot_addition_window()
        self.toplevel.destroy()


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
