import numpy as np
from scipy.interpolate import PchipInterpolator
import pandas as pd
import tkinter.ttk

from models.base_classes import ITU, Model


# definition of the urban templates:

# Number of buildings used in the vector
q = np.linspace(0, 1, 200)


# London building definition, using points in the cdf presented in the ITU 2402
cdfHLondon = np.array(
    [[0, 0], [8, 1e-3], [15, 0.05], [18, 0.09], [20, 0.3], [25, 0.5], [40, 0.9], [60, 0.93], [85, 0.97],
     [150, 0.9701],
     [151, 0.98], [170, 1]])
cdfD1London = np.array([[0, 0], [10, 0.5], [25, 0.8], [50, 0.91], [100, 0.975], [150, 0.98], [350, 1]])
cdfD2London = np.array(
    [[0, 0], [10, 1e-3], [25, 0.1], [50, 0.35], [90, 0.8], [100, 0.85], [150, 0.95], [200, 0.98], [350, 1]])

# creates interpolators
IPH = PchipInterpolator(cdfHLondon[:, 1], cdfHLondon[:, 0])
IPD1 = PchipInterpolator(cdfD1London[:, 1], cdfD1London[:, 0])
IPD2 = PchipInterpolator(cdfD2London[:, 1], cdfD2London[:, 0])

sdhL = pd.Series(index=q, data=IPH(q))
sd2L = pd.Series(index=q, data=IPD2(q))
sd1L = pd.Series(index=q, data=IPD1(q))

urban_template_london = {'Db1': sd1L.values, 'Db2': sd2L.values, 'Hb': sdhL.values}

# Melbourne building definition, using points in the cdf presented in the ITU 2402

cdfDb1Melbourne = np.array(
    [[0, 0], [8.3, 0.2], [19, 0.5], [45.5, 0.8], [82, 0.9], [100, 0.95], [150, 0.972], [200, 0.985], [350, 1]])
cdfDb2Melbourne = np.array(
    [[0, 0], [16.7, 0.01], [50, 0.3], [60.3, 0.4], [70.5, 0.47], [70.51, 0.5], [100, 0.7], [120.5, 0.8], [139.7, 0.9],
     [150, 0.925], [200, 0.975], [350, 1]])
cdfHMelbourne = np.array(
    [[0, 0], [3, 0.008], [5.7, 0.1], [9.7, 0.2], [12.3, 0.3], [15, 0.4], [20, 0.5], [24.7, 0.63], [30, 0.64],
     [31, 0.68], [34, 0.7], [36.7, 0.71], [40, 0.75], [42.7, 0.8], [49, 0.825], [59, 0.83], [60, 0.835],
     [65.7, 0.83501], [74, 0.897], [95.3, 0.9], [106.7, 0.92], [107, 0.95], [150, 0.951], [160, 0.986], [180, 1]])

# creates interpolators

IPHM = PchipInterpolator(cdfHMelbourne[:, 1], cdfHMelbourne[:, 0])
IPD1M = PchipInterpolator(cdfDb1Melbourne[:, 1], cdfDb1Melbourne[:, 0])
IPD2M = PchipInterpolator(cdfDb2Melbourne[:, 1], cdfDb2Melbourne[:, 0])

sdhM = pd.Series(index=q, data=IPHM(q))
sd2M = pd.Series(index=q, data=IPD2M(q))
sd1M = pd.Series(index=q, data=IPD1M(q))

urban_template_melbourne = {'Db1': sd1M.values, 'Db2': sd2M.values, 'Hb': sdhM.values}

urban_templates = {"london": urban_template_london, "melbourne": urban_template_melbourne}


def compute_models(N: int = 10000, f: float = 30.0, Hs: float = 5.0, theta: float = 40.0,
                   city: str = "london") -> dict:
    """
    Model described in the ITU 2402 description.

    Parameters
    ----------
    N : int, optional
        number of points in the simulation
    f : float, optional
        frequency used in the simulation
    Hs : float, optional
        height of the station
    theta : float, optional
        angle, in degrees
    city : str, optional
        data of the city used

    Raises
    ------
    ValueError


    Returns
    -------
        a dictionary containing "clutter loss", "diffraction loss" and "reflection loss" model values

    """
    theta = np.array([theta])

    # Parameters defined in page 8 of ITU 2402
    Kdr = 0.5
    Kdh = 1.5
    Khc = 0.3
    Krc = 3
    Krs = 15
    Krm = 8

    # Generation of the city, section 4.4

    Db1_vect = urban_templates[city]['Db1']
    Db2_vect = urban_templates[city]['Db2']
    Hb_vect = urban_templates[city]['Hb']

    # Generating the buildings for the simulation, section 5.4.1

    Db1 = np.quantile(Db1_vect, np.random.rand(N), interpolation='higher')
    Db2 = np.quantile(Db2_vect, np.random.rand(N), interpolation='higher')
    Db12 = Db2 - Db1

    pr13 = 1 - Kdr * (1 + np.random.rand(N))
    pr23 = 1 - Kdr * (1 + np.random.rand(N))
    pr34 = 1 - Kdr * (1 + np.random.rand(N))

    Dr13 = np.quantile(Db1_vect, pr13, interpolation='higher')
    Dr23 = np.quantile(Db1_vect, pr23, interpolation='higher')
    Dr34 = np.quantile(Db1_vect, pr34, interpolation='higher')

    # Generating the roof heights, section 5.4.2

    Hc = np.quantile(Hb_vect, Khc, interpolation='higher')

    Hb1 = np.quantile(Hb_vect, np.random.rand(N), interpolation='higher')
    Hb2 = np.quantile(Hb_vect, np.random.rand(N), interpolation='higher')
    Hb1s = Hb1 - Hs
    Hb2s = Hb2 - Hs

    Rdh = Kdh * (np.median(Db1_vect) / np.median(Hb_vect))

    if Rdh > 1:
        Hb1s[Hb1s > Hc] = Hc + (Hb1s[Hb1s > Hc] - Hc) / Rdh
        Hb2s[Hb2s > Hc] = Hc + (Hb2s[Hb2s > Hc] - Hc) / Rdh

    Hb3s = np.quantile(Hb_vect, np.random.rand(N), interpolation='higher') - Hs
    Hb4s = np.quantile(Hb_vect, np.random.rand(N), interpolation='higher') - Hs

    # Calculation of the diffraction loss, section 5.5

    lambd = 0.3 / f

    Hrs1 = hray(0, Db1, theta)
    nu1 = nu_calcul(Db1, Hb1, Hrs1, lambd, Hs)

    Ld1 = J(nu1)

    Hrs2 = hray(Hrs1, Db12, theta)
    nu2 = nu_calcul(Db2, Hb2, Hrs2, lambd, Hs)

    Ld2 = J(nu2)

    Ld = 10 * np.log10((10 ** (0.1 * Ld1) + 10 ** (0.1 * Ld2)) * (1 + Ld1 + Ld2) / (2 + Ld1 + Ld2))

    # Calculation of the reflexion loss, section 5.6

    # Here we take back the real heights of the buildings
    Hb1s = Hb1 - Hs
    Hb2s = Hb2 - Hs

    # Here we calculate the ray height
    Hrs3_1 = hray(Hrs1, Dr13, theta)
    Hrs3_2 = hray(Hrs2, Dr23, theta)
    Hrs4_1 = hray(Hrs3_1, Dr34, theta)
    Hrs4_2 = hray(Hrs3_2, Dr34, theta)

    # Initialization of the number of reflexion
    # The following calculations refers to the figure 5 of ITU 2402
    Nr = np.zeros([N, 1])

    # First case, the ray is reflecting of the building B1
    Nr[Hrs1 < Hb1s[:,None]] += 1
    
    # Then we check if there is a reflexion on the buildings B3 or B4
    Nr[(Nr == 1) & (Hrs3_1 < Hb3s[:,None])] += 1
    Nr[(Nr == 2) & (Hrs4_1 < Hb4s[:,None])] = 0


    # A trick to not use the cases already used previously
    # For exemple, if a ray is reflected on the B1 but not on the B2, B3 and B4,
    # its value in the vector Nr is 1, but if the condition Hrs3_2 < Hb3s
    # is true, the value will be increment, and we don't want that
    # so we add 5 to all the cases we already processed to not modify them accidently
    Nr[Nr != 0] += 5  

    # Then we process to the second case, the ray is reflecting of the building B2
    Nr[(Nr == 0) & (Hrs2 < Hb2s[:,None])] += 1
    Nr[(Nr == 1) & (Hrs3_2 < Hb3s[:,None])] += 1
    Nr[(Nr == 2) & (Hrs4_2 < Hb4s[:,None])] = 0

    # At the end, we put back the real number of reflexion
    Nr[Nr > 3] -= 5

    Llof = Krm - Krs * np.log10(f / Krc)
    Lr = 10 * np.log10(10 ** (0.1 * Krm) + 10 ** (0.1 * Llof))

    # Calculation of the clutter loss, section 5.7

    p = np.random.rand(N)
    # In order to randomize Reflexion coeff
    coeff = (-np.log(1 - p)) ** 0.5 / 0.833
    
    Lc = Ld.copy()
    
    Lc[Nr == 1] = -10 * np.log10(
        10 ** (0.1 * (-Ld[Nr == 1])) + 10 ** (0.1 * (-1 * Lr * np.resize(coeff, [N, 1])[:, :][Nr == 1])))
    Lc[Nr == 2] = -10 * np.log10(
        10 ** (0.1 * (-Ld[Nr == 2])) + 10 ** (0.1 * (-2 * Lr * np.resize(coeff, [N, 1])[:, :][Nr == 2])))
    
    # Here we isolate the reflexnio loss, in order to be able to draw it
    Lossr = np.zeros(Lc.shape)
    Lossr[Nr == 0] = 0
    Lossr[Nr == 1] = -10 * np.log10(10 ** (0.1 * (-1 * Lr * np.resize(coeff, [N, 1])[:, :][Nr == 1])))
    Lossr[Nr == 2] = -10 * np.log10(10 ** (0.1 * (-2 * Lr * np.resize(coeff, [N, 1])[:, :][Nr == 2])))

    values = {}
    # Clutter loss display (Lc)
    tmp_x = np.sort(Lc[:, 0])
    tmp_y = np.array(range(N)) / float(N)
    values["clutter loss"] = {"x": tmp_x, "y": tmp_y, "label": f"{str(theta[0])} degrés"}

    # Diffraction loss display (Ld)
    tmp_x = np.sort(Ld[:, 0])
    values["diffraction loss"] = {"x": tmp_x, "y": tmp_y, "label": f"{str(theta[0])} degrés"}

    # Reflexion loss display (Lr)
    tmp_x = np.sort(Lossr[:, 0])
    values["reflection loss"] = {"x": tmp_x, "y": tmp_y, "label": f"{str(theta[0])} degrés"}

    return values


class ITU2402(ITU):

    def __init__(self):
        name = "A method to predict the statistics of clutter loss for earth-space and aeronautical paths"
        ITU_number = 2402
        tags = ["clutter loss", "earth-space paths", "statistics"]

        self.param_model = {
            "N": (10000, int, "optional"),
            "f": (30.0, float, "optional"),
            "Hs": (5.0, float, "optional"),
            "theta": (40.0, float, "optional"),
            "city": ([city for city in urban_templates.keys()], tkinter.ttk.Combobox, "mandatory")
        }

        self.mappings = {
            "french":
                {  # basic localization
                    "f": "fréquence (GHz)",
                    "theta": "angle d'élévation (°)",
                    "N": "nombre de points simulés",
                    "Hs": "hauteur de la station au dessus du sol",
                    "city": "ville"
                }
        }

        self.models = {1: Model(self.model_1,
                                "Modélisation du clutter loss",
                                "clutter loss (dB)",
                                "pourcentage d'emplacement",
                                self.param_model,
                                mappings=self.mappings),
                       2: Model(self.model_2,
                                "Modélisation des pertes par diffraction",
                                "pertes de diffraction (dB)",
                                "pourcentage d'emplacement",
                                self.param_model,
                                mappings=self.mappings),
                       3: Model(self.model_3,
                                "Modélisation des pertes par réflexion",
                                "pertes par réflexion (dB)",
                                "pourcentage d'emplacement",
                                self.param_model,
                                mappings=self.mappings)
                       }

        ITU.__init__(self, name, ITU_number, tags, model_amount=len(self.models))

    def model_1(self, N: int = 10000, f: float = 30.0, Hs: float = 5.0, theta: float = 40.0, city: str = "london") -> (
            np.array, np.array, str):
        values = compute_models(N, f, Hs, theta, city)["clutter loss"]
        return values["x"], values["y"], values["label"]

    def model_2(self, N: int = 10000, f: float = 30.0, Hs: float = 5.0, theta: float = 40.0, city: str = "london") -> (
            np.array, np.array, str):
        values = compute_models(N, f, Hs, theta, city)["diffraction loss"]
        return values["x"], values["y"], values["label"]

    def model_3(self, N: int = 10000, f: float = 30.0, Hs: float = 5.0, theta: float = 40.0, city: str = "london") -> (
            np.array, np.array, str):
        values = compute_models(N, f, Hs, theta, city)["reflection loss"]
        return values["x"], values["y"], values["label"]



def hray(Hrsx, Dxy, angle):
    """
    Parameters
    ----------

    Hrsx : height above the station at the starting point (N,Ntheta)
    Dxy : Horizontal distance (,N)
    angle : elevation angle in degrees (,Ntheta)

    Returns
    -------

    Hray : Height deviation (N,Ntheta)

    Formula (10) of ITU-R P-2402
    """
    angle = (angle * np.pi) / 180
    return Hrsx + Dxy[:,None] * np.tan(angle[None,:])


def nu_calcul(Db, Hb, Hrs, Lambda, Hs=5):
    """


    Parameters
    ----------
    Db : vector of distance (np.array)
    Hb : vector of height (np.array)
    Hrs : table of distance (fonction of theta) (np.array)
    Lambda : lambda
    Hs : station height above ground level (m) (int)

    Returns
    -------
    nu : calculation of nu

    Formula (12) of ITU-R P-2402

    """
    Ro = (Hb[:,None] - Hs - Hrs) / (np.sqrt(Db[:,None] ** 2 + Hrs ** 2))
    ho = Ro * Db[:,None]
    do = np.sqrt(Db[:,None] ** 2 + Hrs ** 2) + Ro * Hrs

    nu = 2 * np.sqrt((np.sqrt(do ** 2 + ho ** 2) - do) / Lambda) * np.sign(ho)
    return nu


def J(nu):
    """
    Parameters
    ----------
    nu : parameter used to calculate diffraction loss

    Returns
    -------
    The diffraction loss

    Formula (11) of ITU-R P-2402
    """
    R = 6.9 + 20 * np.log10(np.sqrt((nu - 0.1) ** 2 + 1) + nu - 0.1)
    R[nu < -0.78] = 0
    return R
