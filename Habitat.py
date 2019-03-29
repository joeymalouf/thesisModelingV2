from __future__ import absolute_import, print_function
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

import numpy as np 
import scipy.signal 
import random 
from fast_space import FastMultiGrid

from s_cerevisiae import S_Cerevisiae
from c_reinhardtii import C_Reinhardtii

import pyopencl as cl
import gputools

class Habitat(Model):
    def __init__(self, s_cerevisiae, c_reinhardtii, CO2, NO2, C6H12O6, KNO2, pH, width, height, time_scale, steps):
        
        ### initialize Model, grid, and scedule ###
        super().__init__()
        self.time_scale = time_scale
        self.grid = FastMultiGrid(width, height, False)
        self.schedule = RandomActivation(self)
        self.running = True
        self.s_cerevisiae_id = -1
        self.c_reinhardtii_id = -1

        ### initialize matrix for holding yeast and alga information ###
        # these matrices are created so that GPU computing is easy
        # they are essentially a sparse matrix for the location of the agents
        # [0] carbon
        # [1] nitrogen
        # [2] x 
        # [3] y
        # [][n] -- n is the species_id

        self.s_cerevisiae_matrix = np.array([[],[],[],[]])
        self.c_reinhardtii_matrix = np.array([[],[],[],[]])

        
        ### set values changeable by users ###

        self.s_cerevisiae = s_cerevisiae
        self.c_reinhardtii = c_reinhardtii
        self.pH = pH
        self.steps = steps
        self.width = width
        self.height = height

        self.CO2 = np.full((width,height), CO2, dtype=np.float64)
        self.NO2 = np.full((width,height), NO2, dtype=np.float64)
        self.C6H12O6 = np.full((width,height), C6H12O6, dtype=np.float64)
        self.KNO2 = np.full((width,height), KNO2, dtype=np.float64)
        self.pH = np.full((width,height), pH, dtype=np.float64)

        ### diffusion filter ###

        self.filter = np.array([[.0125, .0125, .0125],
                [.0125, .9, .0125],
                [.0125, .0125, .0125]])
 

        ### all basic values hardcoded here ###
        


        ### setup values for agents ###
        # These values are here instead of in the agent classes so they only have to be calculated once

        self.s_cerevisiae_information = self.create_s_cerevisiae_information()
        self.c_reinhardtii_information = self.create_c_reinhardtii_information()
         
        ### Place agents into the grid ###

        for _ in range(self.s_cerevisiae):
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.width)
            yeast = S_Cerevisiae(self.next_id(), self.s_cerevisiae_next_id(), self)
            self.schedule.add(yeast)
            self.grid.place_agent(yeast, (x, y))
            self.s_cerevisiae_matrix_add(x, y)

        for _ in range(self.c_reinhardtii):
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.width)
            alga = C_Reinhardtii(self.next_id(), self.c_reinhardtii_next_id(), self)
            self.schedule.add(alga)
            self.grid.place_agent(alga, (x, y))
            self.c_reinhardtii_matrix_add(x, y)
            
        ### setup data collection ###
        
        self.datacollector = DataCollector(
            model_reporters = {
                "S. Cerevisiae":"s_cerevisiae", 
                "C. Reinhardtii":"c_reinhardtii",
                "pH":"pH",
                "CO2": get_CO2,
                "NO2": get_CO2,
                "KN02": get_KNO2,
                "C6H12O6": get_C6H12O6
            }
        )
        self.datacollector.collect(self)

        ### setup GPU context and queue ###

        platforms = cl.get_platforms()
        gpu_device = platforms[0].get_devices(cl.device_type.GPU)[0]
        self.context = cl.Context([gpu_device])

        ## begin steps ###

        self.step()

    def step(self):
        if (self.schedule.steps > self.steps):
            self.runnng = False 

        ### do convolutions for pH and molecules ###



        ### do ingest/excrete for agents ###

    def create_s_cerevisiae_information(self):
        return []

    def create_c_reinhardtii_information(self):
        return []

    def s_cerevisiae_next_id(self):
        self.s_cerevisiae_id += 1
        return self.s_cerevisiae_id

    def c_reinhardtii_next_id(self):
        self.c_reinhardtii_id += 1
        return self.c_reinhardtii_id

    def s_cerevisiae_matrix_add(self, x, y):
        self.s_cerevisiae_matrix = np.append(
            self.s_cerevisiae_matrix, 
            [[self.s_cerevisiae_C],[self.s_cerevisiae_N],[x],[y]], 
            axis=1
        )

    def c_reinhardtii_matrix_add(self, x, y):
        self.c_reinhardtii_matrix = np.append(
            self.c_reinhardtii_matrix, 
            [[self.c_reinhardtii_C],[self.c_reinhardtii_N],[x],[y]], 
            axis=1
        )
        

def get_CO2(model):
    return model.CO2.sum()

def get_C6H12O6(model):
    return model.C6H12O6.sum()

def get_NO2(model):
    return model.NO2.sum()

def get_KNO2(model):
    return model.KNO2.sum()

def get_pH(model):
    return (model.pH.sum() / (model.width*model.height ))


        