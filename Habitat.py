from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

import numpy as np 
import scipy.signal 
from fast_space import FastMultiGrid

class Habitat(Model):
    def __init__(self, s_cerevisiae, c_reinhardtii, CO2, NO2, C6H12O6, KNO2, pH, width, height, time_scale, steps):
        super().__init__()
        self.s_cerevisiae = s_cerevisiae
        self.c_reinhardtii = c_reinhardtii
        self.pH = pH
        self.time_scale = time_scale
        self.grid = FastMultiGrid(width, height, False)
        self.schedule = RandomActivation(self)
        self.running = True
        self.steps = steps

        # diffusion filter #

        self.filter = np.array([[.0125, .0125, .0125],
                [.0125, .9, .0125],
                [.0125, .0125, .0125]])
 
        self.CO2 = np.full((width,height), CO2, dtype=np.float64)
        self.NO2 = np.full((width,height), NO2, dtype=np.float64)
        self.C6H12O6 = np.full((width,height), C6H12O6, dtype=np.float64)
        self.KNO2 = np.full((width,height), KNO2, dtype=np.float64)

        self.s_cerevisiae_information = self.create_s_cerevisiae_information()
        self.c_reinhardtii_information = self.create_c_reinhardtii_information()

        ###### all basic values hardcoded here ######
         


    def create_s_cerevisiae_information(self):
        return []

    def create_c_reinhardtii_information(self):
        return []