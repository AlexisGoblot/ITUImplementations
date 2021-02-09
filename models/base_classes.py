# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np

class Model:
    """
    Class used to represent a Model with its figure
    """
    def __init__(self, model_function, title, xlabel, ylabel, xscale="linear", yscale="linear", xlim=None, ylim=None):
        self.model_function = model_function
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.xscale = xscale
        self.yscale = yscale
        self.xlim = xlim
        self.ylim = ylim
        self.figure = None

    
    def plot(self, x, y, label):
        """
        plot on the figure of the Model object
            
        Returns
        -------
        None.

        """
        
        #delaying the figure creation to avoid additional bugged figures
        if self.figure is None:
            self.figure = self.init_figure()
        else:
            plt.figure(self.figure.number)
            
        plt.plot(x ,y ,label=label)
       
        
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
        
        
class ITU:
    """
    unitary test:
        
    >>> itu = ITU("nom", 1, ["tag"])
    >>> repr(itu)
    'Recommandation ITU 1: nom'
    >>> str(itu)
    'Recommandation ITU 1: nom'
    """
    def __init__(self, name, ITU_number, tags):
        self.name = name
        self.ITU_number = ITU_number
        self.tags = tags
        
        
    def __repr__(self):
        return (f"Recommandation ITU {self.ITU_number}: {self.name}")
    
    
    def __str__(self):
        return self.__repr__()
    
if __name__ == "__main__":
    from doctest import testmod
    testmod(verbose=True)