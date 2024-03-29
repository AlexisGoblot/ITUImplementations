# -*- coding: utf-8 -*-

# MIT License
# 
# Copyright (c) 2021 Guillaume Evain, Alexis Goblot, Luc Gorjux and Thomas Lebreton
#                    Students at ESIR (Rennes) 
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import numpy as np
import scipy.stats as st
from models.base_classes import ITU, Model
from tkinter import ttk


def cotg(x):
    return np.cos(x) / np.sin(x)


class ITU2108(ITU):
    """
    
    This is the class that implements the ITU 2108 recommendation
    
    """

    def __init__(self):
        name = "Prévision de l'affaiblissement dû à des groupes d'obstacles"
        ITU_number = 2108
        tags = ["affaiblissement", "obstacles"]
        ITU.__init__(self, name, ITU_number, tags, model_amount=3)

        # statistic laws used in model_2 and model_3
        self.N = st.norm()
        self.Q = self.N.isf
        self.param_model_1 = {
            "R": (0, int, "mandatory"),
            "env": (["Eau/mer", "Zone dégagée/rurale", "Zone suburbaine",
                     "Zone urbaine/boisée/forêt", "Zone urbaine dense"], ttk.Combobox, "mandatory"),
            "f": (1.5, float, "optional"),
            "ws": (27, int, "optional"),
            "h_size": (1000, int, "optional")
        }

        self.param_model_2 = {
            "f": (30, int, "optional"),
            "d_size": (1000, int, "optional"),
            "correction_one_side": (False, bool, "optional")
        }

        self.param_model_3 = {
            "theta": (10, int, "optional"),
            "f": (30, int, "optional"),
            "p_size": (100, int, "optional")
        }

        self.mappings = {
            "french":
                {  # basic localization
                    "f": "fréquence (GHz)",
                    "p_size": "nombre d'éléments",
                    "d_size": "nombre d'éléments",
                    "h_size": "nombre d'éléments",
                    "ws": "largeur de rue (m)",
                    "env": "environnement",
                    "R": "hauteur représentative du groupe d'obstacle (m)",
                    "theta": "angle d'élévation (°)",
                    "correction_one_side": "correction à seulement une extrémité?"
                }
        }

        self.models = {1: Model(self.model_1,
                                "Modèle de correction de la hauteur en fonction du gain du terminal",
                                "Hauteur d'antenne (m)",
                                "Affaiblissement supplémentaire (dB)",
                                self.param_model_1,
                                mappings=self.mappings),

                       2: Model(self.model_2,
                                "Modèle statistique de l'affaiblissement dû à un groupe \nd'obstacles pour des trajets de Terre",
                                "distance (km)",
                                "valeur médiane des affaiblissements (dB)",
                                self.param_model_2,
                                xscale="log",
                                mappings=self.mappings),

                       3: Model(self.model_3,
                                "Modèle statistique d'affaiblissement dû à un groupe d'obstacles \npour un trajet Terre-espace et pour les services aéronautiques",
                                "Lces (dB)",
                                "Pourcentage d'emplacements",
                                self.param_model_3,
                                xlim=(-5, 70),
                                mappings=self.mappings)
                       }

    def model_1(self, R: int, env: str, f: float = 1.5, ws: int = 27, h_size: int = 1000) -> (
            np.array, np.array, str):
        """
        First model described in the ITU 2108 description.

        Parameters
        ----------
        R : int
            height of the obstacle group (m)
        env : str
            Name of the environment.
        f : float, optional
            frequency used (GHz). The default is 1.5.
        ws : int, optional
            width of the road (m). The default is 27.
        h_size : int, optional
            number of values in the output arrays. The default is 1000.

        Raises
        ------
        ValueError
            the frequency parameter is not valid.

        Returns
        -------
        h : numpy.array
            height of the antenna
        A_h : numpy.array
            additional attenuation (dB)
        label : str
            name of the curve.

        """
        f_min, f_max = 0.03, 3
        if f < f_min or f > f_max:
            raise ValueError(f"la fréquence doit être comprise entre {f_min} et {f_max} GHz")

        h = np.linspace(R, 100, h_size)

        h_diff = R - h
        theta_clut = np.arctan(h_diff / ws)
        K_nu = 0.342 * (f ** 0.5)
        v = K_nu * (h_diff * theta_clut) ** 0.5
        J = 6.9 + 20 * np.log10(((v - 0.1) ** 2 + 1) ** 0.5 + v - 0.1)
        K_h2 = 21.8 + 6.2 * np.log10(f)
        equation_2b = env in ["Eau/mer", "Zone dégagée/rurale"]

        if not equation_2b:
            A_h = J - 6.03
        else:
            A_h = - K_h2 * np.log10(h / R)

        label = f"{env}: R = {R}m, f = {f}GHz"

        return h, A_h, label

    def model_2(self, f: int = 30, d_size: int = 1000, correction_one_side: bool = False) -> (np.array, np.array, str):
        """
        Second model of the ITU 2108 Description

        Parameters
        ----------
        f : int, optional
            frequency used (GHz). The default is 30.
        d_size : int, optional
            size of the output x array. The default is 1000.
        correction_one_side : bool, optional
            boolean used to determine the correct d_min, (see below). 
            The default is False.

        Raises
        ------
        ValueError
            the frequency parameter is not valid

        Returns
        -------
        d : numpy.array
            total length of the flight.
        Lctt : numpy.array
            median value of the additional attenuations.
        label : str
            name of the curve.

        """

        # check if the parameters are in the validity range of the model
        f_min, f_max = 2, 67
        if f < f_min or f > f_max:
            raise ValueError(f"la fréquence doit être comprise entre {f_min} et {f_max} GHz")

        d_min = 0.25 if correction_one_side else 1

        d = np.linspace(d_min, 100, d_size)
        # value to get median curves
        p = 0.5

        Ll = 23.5 + 9.6 * np.log10(f)
        Ls = 32.98 + 23.9 * np.log10(d) + 3 * np.log10(f)
        Lctt = -5 * np.log10(10 ** (-0.2 * Ll) + 10 ** (-0.2 * Ls)) - 6 * self.Q(p)

        label = f"{f} GHz"

        return d, Lctt, label

    def model_3(self, theta: int = 10, f: int = 30, p_size: int = 100) -> (np.array, np.array, str):
        """
        Third model of the ITU 2108 specification.

        Parameters
        ----------
        theta : int, optional
            Elevation angle (°). The default is 10.
        f : int, optional
            frequency used (GHz). The default is 30.
        p_size : int, optional
            size of the output x array. The default is 100.

        Raises
        ------
        ValueError
            the frequency or the elevation angle is not valid

        Returns
        -------
        LCES : numpy.array
            attenuation caused by an obstacle group for an Earth - satellite flight.
        p : numpy.array
            percentage of the slots being higher that the obstacle group.
        label : str
            label of the curve.

        """

        # check if the parameters are in the validity range of the model
        f_min, f_max = 10, 100
        if f < f_min or f > f_max:
            raise ValueError(f"la fréquence doit être comprise entre {f_min} et {f_max} GHz")

        theta_min, theta_max = 0, 90
        if theta < 0 or theta > 90:
            raise ValueError(f"l'angle théta doit être compris entre {theta_min} et {theta_max}°")

        # params defined for the model
        p = np.linspace(0, 1, p_size)
        K1 = 93 * (f ** 0.175)
        A1 = 0.05

        # params used for readability
        a = (A1 * ((90 - theta) / 90) + np.pi * theta / 180)
        b = 0.5 * (90 - theta) / 90

        # compute the resulting pdf
        LCES = (-K1 * np.log(1 - p) * cotg(a)) ** b - 1 - 0.6 * self.Q(p)

        label = f"f={f}GHz et {theta}°"

        return LCES, 100 * p, label


if __name__ == "__main__":

    # ignore runtime warnings throwns by numpy
    import warnings

    warnings.filterwarnings("ignore", category=RuntimeWarning)

    # launch unitary tests
    from doctest import testmod

    testmod(verbose=True)
    # class instantiation
    itu = ITU2108()

    # use the 3rd model
    mod3 = itu.models[3]
    for x in range(0, 91, 10):
        mod3.evaluate(theta=x, plot=True)
    mod3.show()

    # use the 2nd model
    mod2 = itu.models[2]
    Lfreq = [2, 3, 6, 16, 40, 67]  # GHz
    for f in Lfreq:
        mod2.evaluate(f=f, correction_one_side=True, plot=True)
    mod2.show()

    # use the first model
    mod1 = itu.models[1]
    R_dict = {
        "Eau/mer": (10, True),
        "Zone dégagée/rurale": (10, True),
        "Zone suburbaine": (10, False),
        "Zone urbaine/boisée/forêt": (15, False),
        "Zone urbaine dense": (20, False)
    }

    for key, value in R_dict.items():
        mod1.evaluate(value[0], value[1], key, f=2, plot=True)
    mod1.show()

    # todo: verify model #1
