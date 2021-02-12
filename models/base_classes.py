# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import io


class Model:
    """
    Class used to represent a Model with its figure
    """

    def __init__(self, model_function, title, xlabel, ylabel, parameters_desc, xscale="linear", yscale="linear",
                 xlim=None, ylim=None):
        self.model_function = model_function
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xscale = xscale
        self.yscale = yscale
        self.xlim = xlim
        self.ylim = ylim
        self.figure = None
        self.parameters_desc = self.check_param(parameters_desc)  # dict name <-> (value, type, type of parameter)

    def check_param(self, parameters_desc):
        """method to check if the default parameter description has no issue when a Model object is instanciated"""
        errored_params = []
        for k, v in parameters_desc.items():

            # check for fixed length
            if len(v) != 3:
                errored_params.append(k)
                continue

            # check for correct parameter type
            if not isinstance(v[0], v[1]):
                errored_params.append(k)

        # if at least one parameter is errored
        if len(errored_params) != 0:
            raise TypeError(f'parameters {", ".join(errored_params)} are wrongly set')
        return parameters_desc

    def plot(self, x, y, label):
        """
        plot on the figure of the Model object
            
        Returns
        -------
        None.

        """

        # delaying the figure creation to avoid additional bugged figures
        if self.figure is None:
            self.figure = self.init_figure()
        else:
            plt.figure(self.figure.number)

        plt.plot(x, y, label=label)

    def show(self):
        """
        show the figure of the class object
        
        Unitary tests:
            
        >>> model = Model(id, "title", "xlabel", "ylabel")
        >>> model.show()
        Traceback (most recent call last):
          ...
        TypeError: Figure pas encore initialisée, il n'y a rien à afficher
        
        Returns
        -------
        None.

        """

        if self.figure is None:
            raise TypeError("Figure pas encore initialisée, il n'y a rien à afficher")
        plt.figure(self.figure.number)
        plt.legend()
        plt.show()

    def clear(self):
        """
        Reset the figure of the Model object

        Returns
        -------
        None.

        """
        self.figure = self.init_figure()

    def evaluate(self, *args, **kwargs) -> (np.array, np.array, str):
        """
        Evaluate the model in self.model_function.

        Parameters
        ----------
            
        *args : immutable sequence
            positional parameters for self.model_function
        **kwargs : dict
            named parameters for self.model_function

        Returns
        -------
        x : numpy.array<float>
            x array for the plot
        y : numpy.array<float>
            y array for the plot
        label : str
            label of the curve

        """
        plot = False

        if "plot" in kwargs and kwargs["plot"]:
            plot = True
            del kwargs["plot"]

        x, y, label = self.model_function(*args, **kwargs)
        if plot:
            self.plot(x, y, label=label)
        return x, y, label

    def init_figure(self):
        """
        Function used to initialise the internal Figure object of 
        a Model object

        Returns
        -------
        figure : matplotlib.pyplot.Figure
            the internal Figure object of a Model object

        """
        figure = plt.figure()
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.title)
        if not self.xlim is None:
            plt.xlim(self.xlim)

        if not self.ylim is None:
            plt.ylim(self.ylim)

        plt.xscale(self.xscale)
        plt.yscale(self.yscale)
        return figure

    def get_image(self) -> Image:
        """
        get the internal figure as an Image object

        Unitary tests:

        >>> model = Model(id, "title", "xlabel", "ylabel")
        >>> model.get_image()
        Traceback (most recent call last):
          ...
        TypeError: Figure pas encore initialisée, il n'y a rien à afficher

        Returns
        -------
        im : PIL.Image
            the internal figure as an Image object

        """

        if self.figure is None:
            raise TypeError("Figure pas encore initialisée, il n'y a rien à afficher")

        plt.figure(self.figure.number)
        plt.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        im = Image.open(buf)
        im2 = im.copy()  # to avoid the 'ValueError: I/O operation on closed file' later
        buf.close()
        return im2


class ITU:
    """
    unitary test:
        
    >>> itu = ITU("nom", 1, ["tag"])
    >>> repr(itu)
    'Recommandation ITU 1: nom'
    >>> str(itu)
    'Recommandation ITU 1: nom'
    """

    def __init__(self, name, ITU_number, tags, model_amount=0):
        self.name = name
        self.ITU_number = ITU_number
        self.tags = tags
        self.model_amount = model_amount

    def __repr__(self):
        return f"Recommandation ITU {self.ITU_number}: {self.name}"

    def __str__(self):
        return self.__repr__()


if __name__ == "__main__":
    from doctest import testmod

    testmod(verbose=True)
